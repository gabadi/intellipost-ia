"""
MercadoLibre Category Service implementation.

This module provides integration with MercadoLibre's official category API
to detect and validate product categories, avoiding penalties from AI guessing.
"""

import asyncio
import json
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode

import httpx
from cachetools import TTLCache

from modules.content_generation.domain.entities import ProductFeatures
from modules.content_generation.domain.exceptions import (
    CategoryDetectionError,
    CategoryValidationError,
    ExternalServiceError,
    MercadoLibreAPIError,
)
from modules.content_generation.domain.value_objects.category_results import (
    CategoryAttributes,
    CategoryInfo,
    CategoryPredictionResult,
)
from modules.content_generation.domain.value_objects.validation_results import ContentValidationResult
from modules.content_generation.domain.ports.logging.protocols import (
    ContentLoggerProtocol,
)


@dataclass(frozen=True)
class CategorySearchResult:
    """Internal category search result data structure."""
    category_id: str
    category_name: str
    probability: float
    path_from_root: list[CategoryPathNode]


@dataclass(frozen=True)
class CategoryPathNode:
    """Category path node structure."""
    category_id: str
    category_name: str


@dataclass(frozen=True)
class CategoryDetailData:
    """Internal category detail data structure."""
    category_id: str
    category_name: str
    description: str | None = None
    path_from_root: list[CategoryPathNode] = field(default_factory=list)
    children_categories: list[CategoryPathNode] = field(default_factory=list)
    settings: ServiceSettings = field(default_factory=ServiceSettings)
    attribute_types: list[AttributeTypeInfo] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for legacy compatibility."""
        return {
            "id": self.category_id,
            "name": self.category_name,
            "description": self.description,
            "path_from_root": [{"id": node.category_id, "name": node.category_name} for node in self.path_from_root],
            "children_categories": [{"id": node.category_id, "name": node.category_name} for node in self.children_categories],
            "settings": {
                "cache_enabled": self.settings.cache_enabled,
                "timeout_seconds": self.settings.timeout_seconds,
                "max_retries": self.settings.max_retries,
            },
            "attribute_types": [
                {
                    "id": attr.attribute_id,
                    "type": attr.value_type,
                    "required": attr.required,
                    "validation": attr.validation_rules
                } for attr in self.attribute_types
            ]
        }


@dataclass(frozen=True)
class HTTPRequestData:
    """Internal HTTP request data structure."""
    method: str
    url: str
    params: dict[str, Any] | None = None
    data: dict[str, Any] | None = None


@dataclass(frozen=True)
class ServiceSettings:
    """Service configuration settings."""
    cache_enabled: bool = True
    timeout_seconds: int = 30
    max_retries: int = 3
    cache_ttl_seconds: int = 3600
    cache_max_size: int = 1000


@dataclass(frozen=True)
class AttributeTypeInfo:
    """Attribute type information structure."""
    attribute_id: str
    value_type: str
    required: bool = False
    validation_rules: dict[str, str] = field(default_factory=dict)


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
        product_features: ProductFeatures,
        category_hint: str | None = None,
    ) -> CategoryPredictionResult:
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
                cached_result = self.prediction_cache[cache_key]
                # Convert cached dict back to CategoryPredictionResult
                return await self._dict_to_category_prediction_result(cached_result, product_features)

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

            # Create CategoryInfo for predicted category
            predicted_category = await self._create_category_info_from_dict(best_category.to_dict())
            
            # Create alternative predictions
            alternative_predictions = []
            for cat in top_candidates[1:3]:  # Top 2 alternatives
                alt_category = await self._create_category_info_from_dict(cat.to_dict())
                alt_confidence = self._calculate_category_confidence(
                    cat, product_features, search_results
                )
                alternative_predictions.append((alt_category, alt_confidence))
            
            # Create feature importance mapping
            feature_importance = {}
            features_dict = product_features.to_dict_legacy()
            total_features = len(features_dict)
            if total_features > 0:
                base_importance = 1.0 / total_features
                for feature_name in features_dict.keys():
                    # Assign higher importance to core features
                    if feature_name in ["brand", "model", "category"]:
                        feature_importance[feature_name] = min(base_importance * 2, 1.0)
                    else:
                        feature_importance[feature_name] = base_importance
            
            # Determine prediction quality
            prediction_quality = "high" if confidence_score >= 0.8 else \
                                "medium" if confidence_score >= 0.6 else "low"
            
            # Create the result value object
            result = CategoryPredictionResult(
                predicted_category=predicted_category,
                confidence_score=confidence_score,
                alternative_predictions=alternative_predictions,
                prediction_method="ml_api_search",
                model_version="1.0",
                feature_importance=feature_importance,
                analyzed_attributes=CategoryAttributes(),  # Empty for now, will be populated later
                prediction_quality=prediction_quality,
                needs_human_review=confidence_score < 0.6
            )

            # Cache the result (convert to dict for caching)
            cache_result = {
                "category_id": best_category.category_id,
                "category_name": best_category.category_name,
                "category_path": [{"id": node.category_id, "name": node.category_name} for node in best_category.path_from_root],
                "confidence": confidence_score,
                "alternatives": [
                    {
                        "category_id": cat.category_id,
                        "category_name": cat.category_name,
                        "confidence": self._calculate_category_confidence(
                            cat, product_features, search_results
                        ),
                    }
                    for cat in top_candidates[1:3]
                ],
                "prediction_method": "ml_api_search",
                "features_used": list(product_features.to_dict_legacy().keys()),
            }
            self.prediction_cache[cache_key] = cache_result

            self.logger.info(
                f"Category predicted: {best_category.category_name} ({best_category.category_id}) with confidence {confidence_score:.2f}"
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
        product_features: ProductFeatures,
    ) -> ContentValidationResult:
        """
        Validate if category is appropriate for product.

        Args:
            category_id: Category ID to validate
            product_features: Product features

        Returns:
            ContentValidationResult containing validation results

        Raises:
            CategoryValidationError: If validation fails
        """
        try:
            # Get category details - now returns CategoryInfo value object
            category_info = await self.get_category_info(category_id)

            # Check if category allows listings
            # Note: For now we'll check if this is a leaf category as proxy for allowing listings
            if not category_info.is_leaf_category:
                return ContentValidationResult(
                    valid=False,
                    validation_score=0.0,
                    content_quality_score=0.0,
                    validation_errors=["Category does not allow listings (not a leaf category)"],
                    validation_engine="ml_category_service",
                )

            # Get category attributes - now returns CategoryAttributes value object
            category_attributes = await self.get_category_attributes(category_id)

            # Validate required attributes
            validation_errors: list[str] = []
            missing_attributes: list[str] = []

            for attr_name in category_info.required_attributes:
                if not self._has_matching_feature(attr_name, product_features):
                    missing_attributes.append(attr_name)

            if missing_attributes:
                validation_errors.append(
                    f"Missing required attributes: {', '.join(missing_attributes)}"
                )

            # Calculate compatibility score using value objects
            compatibility_score = self._calculate_compatibility_score(
                category_info, category_attributes, product_features
            )

            is_valid = len(validation_errors) == 0
            validation_score = compatibility_score if is_valid else max(0.1, compatibility_score - 0.3)

            return ContentValidationResult(
                valid=is_valid,
                validation_score=validation_score,
                content_quality_score=validation_score,
                validation_errors=validation_errors,
                validation_warnings=[f"Missing {len(missing_attributes)} required attributes"] if missing_attributes else [],
                validation_engine="ml_category_service",
            )

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
    ) -> CategoryAttributes:
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
                cached_response = self.category_cache[cache_key]
                return await self._dict_to_category_attributes(cached_response)

            # Make API request
            url = f"{self.base_url}/categories/{category_id}/attributes"
            response = await self._make_request("GET", url)

            # Cache the result
            self.category_cache[cache_key] = response

            # Convert response to CategoryAttributes value object
            return await self._dict_to_category_attributes(response)

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
    ) -> CategoryInfo:
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
                cached_response = self.category_cache[cache_key]
                return await self._create_category_info_from_dict(cached_response)

            # Make API request
            url = f"{self.base_url}/categories/{category_id}"
            response = await self._make_request("GET", url)

            # Cache the result
            self.category_cache[cache_key] = response

            # Convert response to CategoryInfo value object
            return await self._create_category_info_from_dict(response)

        except Exception as e:
            self.logger.error(f"Error getting category info for {category_id}: {e}")
            raise MercadoLibreAPIError(
                f"Failed to get category info: {str(e)}",
                api_endpoint=f"/categories/{category_id}",
                error_code="INFO_FETCH_FAILED",
            ) from e

    async def _search_categories_by_features(
        self,
        product_features: ProductFeatures,
    ) -> list[CategorySearchResult]:
        """Search for categories based on product features."""
        search_queries = self._generate_search_queries(product_features)

        all_results: list[CategorySearchResult] = []
        for query in search_queries:
            try:
                results = await self._search_categories(query)
                all_results.extend(results)
            except Exception as e:
                self.logger.warning(f"Search query failed: {query}, error: {e}")
                continue

        # Deduplicate results
        unique_results: dict[str, CategorySearchResult] = {}
        for result in all_results:
            if result.category_id and result.category_id not in unique_results:
                unique_results[result.category_id] = result

        return list(unique_results.values())

    async def _search_categories(self, query: str) -> list[CategorySearchResult]:
        """Search categories using MercadoLibre category predictor."""
        try:
            # Use the category predictor API
            url = f"{self.base_url}/sites/{self.site_id}/category_predictor/predict"
            params = {"title": query}

            response = await self._make_request("GET", url, params=params)

            # Extract categories from response
            categories: list[CategorySearchResult] = []
            if "results" in response:
                for result in response["results"]:
                    # Convert path_from_root to typed nodes
                    path_nodes = []
                    for path_item in result.get("path_from_root", []):
                        if isinstance(path_item, dict) and "id" in path_item and "name" in path_item:
                            path_nodes.append(CategoryPathNode(
                                category_id=path_item["id"],
                                category_name=path_item["name"]
                            ))
                    
                    categories.append(
                        CategorySearchResult(
                            category_id=result.get("id", ""),
                            category_name=result.get("name", ""),
                            probability=result.get("probability", 0.0),
                            path_from_root=path_nodes,
                        )
                    )

            return categories

        except Exception as e:
            self.logger.error(f"Error searching categories with query '{query}': {e}")
            return []

    def _generate_search_queries(self, product_features: ProductFeatures) -> list[str]:
        """Generate search queries from product features."""
        queries: list[str] = []

        # Basic product description
        brand = product_features.brand or ""
        model = product_features.model or ""
        category = product_features.category or ""

        if brand and model:
            queries.append(f"{brand} {model}")

        if category:
            queries.append(category)

        if brand:
            queries.append(brand)

        # Technical specs
        specs = product_features.technical_specs
        if specs:
            for key, value in specs.items():
                if value:
                    queries.append(f"{key} {value}")

        # Color and material
        color = product_features.color or ""
        material = product_features.material or ""

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
        categories: list[CategorySearchResult],
        product_features: ProductFeatures,
        category_hint: str | None = None,
    ) -> list[CategorySearchResult]:
        """Rank categories by relevance to product features."""

        def calculate_score(category: CategorySearchResult) -> float:
            score = 0.0

            # Base probability from API
            score += category.probability * 0.4

            # Category hint bonus
            if category_hint:
                if category_hint.lower() in category.category_name.lower():
                    score += 0.3

            # Brand/model matching
            brand = (product_features.brand or "").lower()
            model = (product_features.model or "").lower()
            category_name = category.category_name.lower()

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
        categories: list[CategorySearchResult],
    ) -> list[CategoryDetailData]:
        """Get detailed information for multiple categories."""
        tasks: list[Any] = []
        for category in categories:
            task = self.get_category_info(category.category_id)
            tasks.append(task)

        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)

            detailed_categories: list[CategoryDetailData] = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.warning(
                        f"Failed to get details for category {categories[i].category_id}: {result}"
                    )
                    continue

                # Convert CategoryInfo result to CategoryDetailData
                if hasattr(result, 'category_id'):  # CategoryInfo object
                    detailed_category = CategoryDetailData(
                        category_id=result.category_id,
                        category_name=result.category_name,
                        description=result.description,
                        path_from_root=categories[i].path_from_root,  # Use search result path
                    )
                else:
                    # Fallback: create minimal CategoryDetailData
                    detailed_category = CategoryDetailData(
                        category_id=categories[i].category_id,
                        category_name=categories[i].category_name,
                        path_from_root=categories[i].path_from_root,
                    )
                    
                detailed_categories.append(detailed_category)

            return detailed_categories

        except Exception as e:
            self.logger.error(f"Error getting category details batch: {e}")
            # Return original categories as fallback, converted to CategoryDetailData
            return [
                CategoryDetailData(
                    category_id=cat.category_id,
                    category_name=cat.category_name,
                    path_from_root=cat.path_from_root,
                )
                for cat in categories
            ]

    def _select_best_category(
        self,
        categories: list[CategoryDetailData],
        product_features: ProductFeatures,
    ) -> CategoryDetailData:
        """Select the best category from candidates."""
        if not categories:
            raise CategoryDetectionError("No categories found")

        # For now, return the first category (highest ranked)
        # In a more sophisticated implementation, we could add additional scoring
        return categories[0]

    def _calculate_category_confidence(
        self,
        category: CategoryDetailData,
        product_features: ProductFeatures,
        search_results: list[CategorySearchResult],
    ) -> float:
        """Calculate confidence score for category selection."""
        confidence = 0.0

        # Find original search result for probability
        original_probability = 0.0
        for result in search_results:
            if result.category_id == category.category_id:
                original_probability = result.probability
                break

        # Base confidence from API probability
        confidence += original_probability * 0.4

        # Boost for categories that appear in multiple searches
        appearances = sum(
            1 for result in search_results if result.category_id == category.category_id
        )
        confidence += min(appearances * 0.1, 0.3)

        # Boost for categories with cache enabled (proxy for active)
        if category.settings.cache_enabled:
            confidence += 0.2

        # Boost for categories (assume allow listings for leaf categories)
        confidence += 0.1

        return min(confidence, 1.0)


    def _calculate_compatibility_score(
        self,
        category_info: CategoryInfo,
        category_attributes: CategoryAttributes,
        product_features: ProductFeatures,
    ) -> float:
        """Calculate compatibility score using value objects."""
        score = 0.0

        # Check if category is suitable (leaf category)
        if category_info.is_leaf_category:
            score += 0.5

        # Check attribute compatibility
        total_attributes = len(category_info.allowed_attributes)
        if total_attributes > 0:
            matching_attributes = 0
            for attr_name in category_info.allowed_attributes:
                if self._has_matching_feature(attr_name, product_features):
                    matching_attributes += 1

            attribute_score = matching_attributes / total_attributes
            score += attribute_score * 0.5

        return min(score, 1.0)

    def _has_matching_feature(
        self, attr_id: str, product_features: ProductFeatures
    ) -> bool:
        """Check if product features match a category attribute."""
        # Simple matching logic - in production this would be more sophisticated
        attr_id_lower = attr_id.lower()

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
                feature_value = getattr(product_features, key, None)
                return bool(feature_value)

        return False

    def _create_prediction_cache_key(
        self,
        product_features: ProductFeatures,
        category_hint: str | None = None,
    ) -> str:
        """Create cache key for category prediction."""
        key_data = {
            "features": sorted(product_features.to_dict_legacy().items()),
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

    async def _create_category_info_from_dict(self, category_dict: dict[str, Any]) -> CategoryInfo:
        """Create CategoryInfo value object from API response dict."""
        try:
            # Extract basic info
            category_id = category_dict.get("id", "")
            category_name = category_dict.get("name", "")
            
            # Extract path information
            path_from_root = category_dict.get("path_from_root", [])
            category_path = " > ".join([cat.get("name", "") for cat in path_from_root]) if path_from_root else None
            
            # Determine parent and level
            parent_category_id = None
            level = 0
            if path_from_root and len(path_from_root) > 1:
                parent_category_id = path_from_root[-2].get("id")
                level = len(path_from_root) - 1
            
            # Extract settings
            settings = category_dict.get("settings", {})
            is_leaf_category = not category_dict.get("children_categories", [])
            
            # For now, we'll populate basic attributes
            # In a full implementation, we'd extract these from the ML API response
            allowed_attributes = []
            required_attributes = []
            
            # Extract attributes from category data if available
            if "attribute_types" in category_dict:
                for attr in category_dict["attribute_types"]:
                    attr_id = attr.get("id", "")
                    if attr_id:
                        allowed_attributes.append(attr_id)
                        if attr.get("required", False):
                            required_attributes.append(attr_id)
            
            return CategoryInfo(
                category_id=category_id,
                category_name=category_name,
                category_path=category_path,
                description=category_dict.get("description"),
                parent_category_id=parent_category_id,
                level=level,
                is_leaf_category=is_leaf_category,
                allowed_attributes=allowed_attributes,
                required_attributes=required_attributes,
                ml_category_id=category_id,
                external_mappings={"mercadolibre": category_id}
            )
            
        except Exception as e:
            self.logger.error(f"Error creating CategoryInfo from dict: {e}")
            # Return a minimal valid CategoryInfo
            return CategoryInfo(
                category_id=category_dict.get("id", "unknown"),
                category_name=category_dict.get("name", "Unknown Category"),
                is_leaf_category=True
            )

    async def _dict_to_category_attributes(self, attributes_dict: dict[str, Any]) -> CategoryAttributes:
        """Convert API response dict to CategoryAttributes value object."""
        try:
            from modules.content_generation.domain.value_objects.category_results import CategoryAttribute
            
            attributes = []
            api_attributes = attributes_dict.get("attributes", [])
            
            for attr_data in api_attributes:
                attr_id = attr_data.get("id", "")
                attr_name = attr_data.get("name", attr_id)
                attr_type = self._map_api_attribute_type(attr_data.get("type", "text"))
                required = attr_data.get("required", False)
                
                # Create CategoryAttribute
                category_attr = CategoryAttribute(
                    name=attr_name,
                    value=None,  # No value yet, this is just the attribute definition
                    attribute_type=attr_type,
                    confidence=1.0,  # High confidence for official API attributes
                    importance_weight=0.8 if required else 0.5,
                    source="mercadolibre_api",
                    extraction_method="api_call"
                )
                attributes.append(category_attr)
            
            return CategoryAttributes(
                attributes=attributes,
                extraction_source="mercadolibre_api"
            )
            
        except Exception as e:
            self.logger.error(f"Error creating CategoryAttributes from dict: {e}")
            # Return empty CategoryAttributes
            return CategoryAttributes(extraction_source="mercadolibre_api")

    async def _dict_to_category_prediction_result(
        self, 
        cached_dict: dict[str, Any], 
        product_features: ProductFeatures
    ) -> CategoryPredictionResult:
        """Convert cached dict back to CategoryPredictionResult."""
        try:
            # Create CategoryInfo for the main prediction
            main_category_info = CategoryInfo(
                category_id=cached_dict.get("category_id", ""),
                category_name=cached_dict.get("category_name", ""),
                category_path=" > ".join([cat["name"] for cat in cached_dict.get("category_path", [])]) if cached_dict.get("category_path") else None,
                is_leaf_category=True  # Assume leaf category for predictions
            )
            
            # Create alternative predictions
            alternative_predictions = []
            for alt in cached_dict.get("alternatives", []):
                alt_category_info = CategoryInfo(
                    category_id=alt.get("category_id", ""),
                    category_name=alt.get("category_name", ""),
                    is_leaf_category=True
                )
                alternative_predictions.append((alt_category_info, alt.get("confidence", 0.0)))
            
            # Create feature importance from features used
            feature_importance = {}
            features_used = cached_dict.get("features_used", [])
            if features_used:
                base_importance = 1.0 / len(features_used)
                for feature in features_used:
                    feature_importance[feature] = base_importance
            
            confidence_score = cached_dict.get("confidence", 0.0)
            prediction_quality = "high" if confidence_score >= 0.8 else \
                                "medium" if confidence_score >= 0.6 else "low"
            
            return CategoryPredictionResult(
                predicted_category=main_category_info,
                confidence_score=confidence_score,
                alternative_predictions=alternative_predictions,
                prediction_method=cached_dict.get("prediction_method", "ml_api_search"),
                model_version="1.0",
                feature_importance=feature_importance,
                analyzed_attributes=CategoryAttributes(),
                prediction_quality=prediction_quality,
                needs_human_review=confidence_score < 0.6
            )
            
        except Exception as e:
            self.logger.error(f"Error converting cached dict to CategoryPredictionResult: {e}")
            # Return a minimal valid result
            return CategoryPredictionResult(
                predicted_category=CategoryInfo(
                    category_id="unknown",
                    category_name="Unknown Category",
                    is_leaf_category=True
                ),
                confidence_score=0.0,
                prediction_quality="unknown",
                needs_human_review=True
            )

    def _map_api_attribute_type(self, api_type: str) -> str:
        """Map API attribute type to our standardized types."""
        type_mapping = {
            "string": "text",
            "text": "text", 
            "number": "numeric",
            "integer": "numeric",
            "float": "numeric",
            "boolean": "boolean",
            "list": "list",
            "array": "list"
        }
        return type_mapping.get(api_type.lower(), "text")
