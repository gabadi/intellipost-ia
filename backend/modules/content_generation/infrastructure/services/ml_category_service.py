"""
MercadoLibre Category Service implementation.

This module provides integration with MercadoLibre's official category API
to detect and validate product categories, avoiding penalties from AI guessing.
"""

import asyncio
import json
from typing import Any
from urllib.parse import urlencode

import httpx
from cachetools import TTLCache

from modules.content_generation.domain.exceptions import (
    CategoryDetectionError,
    CategoryValidationError,
    ExternalServiceError,
    MercadoLibreAPIError,
)
from modules.content_generation.domain.ports.logging.protocols import (
    ContentLoggerProtocol,
)


class MLCategoryService:
    """
    MercadoLibre category service implementation.

    This service integrates with MercadoLibre's official category API
    to provide accurate category detection and validation.
    """

    def __init__(
        self,
        logger: ContentLoggerProtocol,
        site_id: str = "MLA",  # Argentina
        timeout_seconds: int = 30,
        max_retries: int = 3,
        cache_ttl_seconds: int = 3600,  # 1 hour
        cache_max_size: int = 1000,
    ):
        """
        Initialize the MercadoLibre category service.

        Args:
            logger: Logger protocol for logging operations
            site_id: MercadoLibre site ID (MLA for Argentina)
            timeout_seconds: Request timeout in seconds
            max_retries: Maximum retry attempts
            cache_ttl_seconds: Cache TTL in seconds
            cache_max_size: Maximum cache size
        """
        self.logger = logger
        self.site_id = site_id
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries

        # Base URL for MercadoLibre API
        self.base_url = "https://api.mercadolibre.com"

        # Initialize HTTP client
        self.client = httpx.AsyncClient(
            timeout=self.timeout_seconds,
            headers={
                "User-Agent": "IntelliPost-AI/1.0",
                "Accept": "application/json",
            },
        )

        # Initialize caches
        self.category_cache: TTLCache = TTLCache(
            maxsize=cache_max_size, ttl=cache_ttl_seconds
        )
        self.prediction_cache: TTLCache = TTLCache(
            maxsize=cache_max_size,
            ttl=cache_ttl_seconds // 2,  # Shorter TTL for predictions
        )

        self.logger.info(f"Initialized ML Category Service for site: {site_id}")

    async def predict_category(
        self,
        product_features: dict[str, Any],
        category_hint: str | None = None,
    ) -> dict[str, Any]:
        """
        Predict MercadoLibre category from product features.

        Args:
            product_features: Extracted product features
            category_hint: Optional category hint

        Returns:
            Dict containing category prediction results

        Raises:
            CategoryDetectionError: If category prediction fails
        """
        try:
            # Create cache key
            cache_key = self._create_prediction_cache_key(
                product_features, category_hint
            )

            # Check cache first
            if cache_key in self.prediction_cache:
                self.logger.debug("Category prediction cache hit")
                return self.prediction_cache[cache_key]

            # Search for categories based on product features
            search_results = await self._search_categories_by_features(product_features)

            # Rank categories by relevance
            ranked_categories = self._rank_categories(
                search_results, product_features, category_hint
            )

            # Get detailed information for top candidates
            top_candidates = await self._get_category_details_batch(
                ranked_categories[:5]
            )

            # Select best category
            best_category = self._select_best_category(top_candidates, product_features)

            # Calculate confidence score
            confidence_score = self._calculate_category_confidence(
                best_category, product_features, search_results
            )

            result = {
                "category_id": best_category["id"],
                "category_name": best_category["name"],
                "category_path": best_category.get("path_from_root", []),
                "confidence": confidence_score,
                "alternatives": [
                    {
                        "category_id": cat["id"],
                        "category_name": cat["name"],
                        "confidence": self._calculate_category_confidence(
                            cat, product_features, search_results
                        ),
                    }
                    for cat in top_candidates[1:3]  # Top 2 alternatives
                ],
                "prediction_method": "ml_api_search",
                "features_used": list(product_features.keys()),
            }

            # Cache the result
            self.prediction_cache[cache_key] = result

            self.logger.info(
                f"Category predicted: {best_category['name']} ({best_category['id']}) with confidence {confidence_score:.2f}"
            )
            return result

        except Exception as e:
            self.logger.error(f"Error predicting category: {e}")
            raise CategoryDetectionError(
                f"Failed to predict category: {str(e)}",
                product_features=product_features,
                error_code="PREDICTION_FAILED",
            ) from e

    async def validate_category(
        self,
        category_id: str,
        product_features: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Validate if category is appropriate for product.

        Args:
            category_id: Category ID to validate
            product_features: Product features

        Returns:
            Dict containing validation results

        Raises:
            CategoryValidationError: If validation fails
        """
        try:
            # Get category details
            category_info = await self.get_category_info(category_id)

            # Check if category allows listings
            if not category_info.get("settings", {}).get("allow_listings", True):
                return {
                    "is_valid": False,
                    "validation_errors": ["Category does not allow listings"],
                    "category_info": category_info,
                }

            # Check if category is active
            if category_info.get("settings", {}).get("status") != "active":
                return {
                    "is_valid": False,
                    "validation_errors": ["Category is not active"],
                    "category_info": category_info,
                }

            # Get category attributes
            category_attributes = await self.get_category_attributes(category_id)

            # Validate required attributes
            validation_errors: list[str] = []
            missing_attributes: list[str] = []

            for attr in category_attributes.get("attributes", []):
                if attr.get("required", False):
                    attr_id = attr.get("id")
                    if attr_id and not self._has_matching_feature(
                        attr_id, product_features
                    ):
                        missing_attributes.append(attr_id)

            if missing_attributes:
                validation_errors.append(
                    f"Missing required attributes: {', '.join(missing_attributes)}"
                )

            # Calculate compatibility score
            compatibility_score = self._calculate_compatibility_score(
                category_info, category_attributes, product_features
            )

            return {
                "is_valid": len(validation_errors) == 0,
                "validation_errors": validation_errors,
                "compatibility_score": compatibility_score,
                "category_info": category_info,
                "required_attributes": [
                    attr
                    for attr in category_attributes.get("attributes", [])
                    if attr.get("required", False)
                ],
                "missing_attributes": missing_attributes,
            }

        except Exception as e:
            self.logger.error(f"Error validating category {category_id}: {e}")
            raise CategoryValidationError(
                f"Failed to validate category: {str(e)}",
                category_id=category_id,
                error_code="VALIDATION_FAILED",
            ) from e

    async def get_category_attributes(
        self,
        category_id: str,
    ) -> dict[str, Any]:
        """
        Get required and optional attributes for a category.

        Args:
            category_id: Category ID

        Returns:
            Dict containing category attributes
        """
        try:
            # Check cache first
            cache_key = f"attributes:{category_id}"
            if cache_key in self.category_cache:
                return self.category_cache[cache_key]

            # Make API request
            url = f"{self.base_url}/categories/{category_id}/attributes"
            response = await self._make_request("GET", url)

            # Cache the result
            self.category_cache[cache_key] = response

            return response

        except Exception as e:
            self.logger.error(
                f"Error getting category attributes for {category_id}: {e}"
            )
            raise MercadoLibreAPIError(
                f"Failed to get category attributes: {str(e)}",
                api_endpoint=f"/categories/{category_id}/attributes",
                error_code="ATTRIBUTES_FETCH_FAILED",
            ) from e

    async def get_category_info(
        self,
        category_id: str,
    ) -> dict[str, Any]:
        """
        Get detailed information about a category.

        Args:
            category_id: Category ID

        Returns:
            Dict containing category information
        """
        try:
            # Check cache first
            cache_key = f"info:{category_id}"
            if cache_key in self.category_cache:
                return self.category_cache[cache_key]

            # Make API request
            url = f"{self.base_url}/categories/{category_id}"
            response = await self._make_request("GET", url)

            # Cache the result
            self.category_cache[cache_key] = response

            return response

        except Exception as e:
            self.logger.error(f"Error getting category info for {category_id}: {e}")
            raise MercadoLibreAPIError(
                f"Failed to get category info: {str(e)}",
                api_endpoint=f"/categories/{category_id}",
                error_code="INFO_FETCH_FAILED",
            ) from e

    async def _search_categories_by_features(
        self,
        product_features: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Search for categories based on product features."""
        search_queries = self._generate_search_queries(product_features)

        all_results: list[dict[str, Any]] = []
        for query in search_queries:
            try:
                results = await self._search_categories(query)
                all_results.extend(results)
            except Exception as e:
                self.logger.warning(f"Search query failed: {query}, error: {e}")
                continue

        # Deduplicate results
        unique_results: dict[str, dict[str, Any]] = {}
        for result in all_results:
            cat_id = result.get("id")
            if cat_id and cat_id not in unique_results:
                unique_results[cat_id] = result

        return list(unique_results.values())

    async def _search_categories(self, query: str) -> list[dict[str, Any]]:
        """Search categories using MercadoLibre category predictor."""
        try:
            # Use the category predictor API
            url = f"{self.base_url}/sites/{self.site_id}/category_predictor/predict"
            params = {"title": query}

            response = await self._make_request("GET", url, params=params)

            # Extract categories from response
            categories: list[dict[str, Any]] = []
            if "results" in response:
                for result in response["results"]:
                    categories.append(
                        {
                            "id": result.get("id"),
                            "name": result.get("name"),
                            "probability": result.get("probability", 0.0),
                            "path_from_root": result.get("path_from_root", []),
                        }
                    )

            return categories

        except Exception as e:
            self.logger.error(f"Error searching categories with query '{query}': {e}")
            return []

    def _generate_search_queries(self, product_features: dict[str, Any]) -> list[str]:
        """Generate search queries from product features."""
        queries: list[str] = []

        # Basic product description
        brand = product_features.get("brand", "")
        model = product_features.get("model", "")
        category = product_features.get("category", "")

        if brand and model:
            queries.append(f"{brand} {model}")

        if category:
            queries.append(category)

        if brand:
            queries.append(brand)

        # Technical specs
        specs = product_features.get("technical_specs", {})
        if specs:
            for key, value in specs.items():
                if value:
                    queries.append(f"{key} {value}")

        # Color and material
        color = product_features.get("color", "")
        material = product_features.get("material", "")

        if color:
            queries.append(f"{category} {color}" if category else color)

        if material:
            queries.append(f"{category} {material}" if category else material)

        # Fallback to general category
        if not queries and category:
            queries.append(category)

        return queries[:5]  # Limit to 5 queries

    def _rank_categories(
        self,
        categories: list[dict[str, Any]],
        product_features: dict[str, Any],
        category_hint: str | None = None,
    ) -> list[dict[str, Any]]:
        """Rank categories by relevance to product features."""

        def calculate_score(category: dict[str, Any]) -> float:
            score = 0.0

            # Base probability from API
            score += category.get("probability", 0.0) * 0.4

            # Category hint bonus
            if category_hint:
                if category_hint.lower() in category.get("name", "").lower():
                    score += 0.3

            # Brand/model matching
            brand = product_features.get("brand", "").lower()
            model = product_features.get("model", "").lower()
            category_name = category.get("name", "").lower()

            if brand and brand in category_name:
                score += 0.2
            if model and model in category_name:
                score += 0.1

            return score

        # Sort by calculated score
        ranked = sorted(categories, key=calculate_score, reverse=True)

        return ranked

    async def _get_category_details_batch(
        self,
        categories: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Get detailed information for multiple categories."""
        tasks: list[Any] = []
        for category in categories:
            task = self.get_category_info(category["id"])
            tasks.append(task)

        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)

            detailed_categories: list[dict[str, Any]] = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.warning(
                        f"Failed to get details for category {categories[i]['id']}: {result}"
                    )
                    continue

                # Merge original category data with detailed info
                result_dict: dict[str, Any] = result if isinstance(result, dict) else {}  # type: ignore[reportUnknownVariableType]
                detailed_category: dict[str, Any] = {**categories[i], **result_dict}
                detailed_categories.append(detailed_category)

            return detailed_categories

        except Exception as e:
            self.logger.error(f"Error getting category details batch: {e}")
            return categories  # Return original categories as fallback

    def _select_best_category(
        self,
        categories: list[dict[str, Any]],
        product_features: dict[str, Any],
    ) -> dict[str, Any]:
        """Select the best category from candidates."""
        if not categories:
            raise CategoryDetectionError("No categories found")

        # For now, return the first category (highest ranked)
        # In a more sophisticated implementation, we could add additional scoring
        return categories[0]

    def _calculate_category_confidence(
        self,
        category: dict[str, Any],
        product_features: dict[str, Any],
        search_results: list[dict[str, Any]],
    ) -> float:
        """Calculate confidence score for category selection."""
        confidence = 0.0

        # Base confidence from API probability
        confidence += category.get("probability", 0.0) * 0.4

        # Boost for categories that appear in multiple searches
        appearances = sum(
            1 for result in search_results if result.get("id") == category.get("id")
        )
        confidence += min(appearances * 0.1, 0.3)

        # Boost for active categories
        if category.get("settings", {}).get("status") == "active":
            confidence += 0.2

        # Boost for categories that allow listings
        if category.get("settings", {}).get("allow_listings", True):
            confidence += 0.1

        return min(confidence, 1.0)

    def _calculate_compatibility_score(
        self,
        category_info: dict[str, Any],
        category_attributes: dict[str, Any],
        product_features: dict[str, Any],
    ) -> float:
        """Calculate compatibility score between category and product."""
        score = 0.0

        # Check if category is suitable for listings
        if category_info.get("settings", {}).get("allow_listings", True):
            score += 0.3

        # Check if category is active
        if category_info.get("settings", {}).get("status") == "active":
            score += 0.2

        # Check attribute compatibility
        total_attributes = len(category_attributes.get("attributes", []))
        if total_attributes > 0:
            matching_attributes = 0
            for attr in category_attributes.get("attributes", []):
                attr_id = attr.get("id")
                if self._has_matching_feature(attr_id, product_features):
                    matching_attributes += 1

            attribute_score = matching_attributes / total_attributes
            score += attribute_score * 0.5

        return min(score, 1.0)

    def _has_matching_feature(
        self, attr_id: str, product_features: dict[str, Any]
    ) -> bool:
        """Check if product features match a category attribute."""
        # Simple matching logic - in production this would be more sophisticated
        attr_id_lower = attr_id.lower()

        # Check direct matches
        if attr_id_lower in product_features:
            return bool(product_features[attr_id_lower])

        # Check common mappings
        mappings = {
            "brand": ["brand", "marca"],
            "model": ["model", "modelo"],
            "color": ["color", "colour"],
            "size": ["size", "tamaño", "talla"],
            "material": ["material"],
            "condition": ["condition", "estado"],
        }

        for key, alternatives in mappings.items():
            if attr_id_lower in alternatives:
                return key in product_features and bool(product_features[key])

        return False

    def _create_prediction_cache_key(
        self,
        product_features: dict[str, Any],
        category_hint: str | None = None,
    ) -> str:
        """Create cache key for category prediction."""
        key_data = {
            "features": sorted(product_features.items()),
            "hint": category_hint,
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return f"prediction:{hash(key_string)}"

    async def _make_request(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make HTTP request with retry logic."""
        for attempt in range(self.max_retries):
            try:
                if method == "GET":
                    if params:
                        url = f"{url}?{urlencode(params)}"
                    response = await self.client.get(url)
                elif method == "POST":
                    response = await self.client.post(url, json=data)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                response.raise_for_status()
                return response.json()

            except httpx.RequestError as e:
                if attempt < self.max_retries - 1:
                    wait_time = (2**attempt) + (attempt * 0.1)
                    self.logger.warning(
                        f"Request failed, retrying in {wait_time}s: {e}"
                    )
                    await asyncio.sleep(wait_time)
                else:
                    raise ExternalServiceError(
                        f"Request failed after {self.max_retries} attempts: {str(e)}",
                        service_name="MercadoLibre API",
                        service_url=url,
                    ) from e
            except httpx.HTTPStatusError as e:
                raise MercadoLibreAPIError(
                    f"HTTP error {e.response.status_code}: {e.response.text}",
                    api_endpoint=url,
                    status_code=e.response.status_code,
                ) from e

        # This should never be reached due to exceptions being raised
        raise ExternalServiceError(
            "Request failed after all retries",
            service_name="MercadoLibre API",
            service_url=url,
        )

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Async context manager exit."""
        await self.close()
