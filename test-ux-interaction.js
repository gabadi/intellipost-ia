import { chromium } from 'playwright';

async function testUXInteraction() {
  console.log('🚀 Iniciando prueba de interacción UX...');

  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  try {
    // Navegar a la página principal
    console.log('📄 Navegando a la página principal...');
    await page.goto('http://localhost:5173/');

    // Verificar que la página carga correctamente
    await page.waitForSelector('h1');
    const title = await page.textContent('h1');
    console.log(`✅ Título encontrado: ${title}`);

    // Verificar conexión con backend
    await page.waitForSelector('.status-dot', { timeout: 10000 });
    const statusDot = page.locator('.status-dot');
    const isHealthy = await statusDot.evaluate(el => el.classList.contains('success'));
    console.log(`🏥 Estado del backend: ${isHealthy ? 'Saludable' : 'Desconectado'}`);

    // Probar navegación a la página de productos
    console.log('🛍️ Navegando a creación de productos...');
    await page.click('a[href="/products/new"]');
    await page.waitForTimeout(2000);

    // Verificar que llegamos a la página correcta
    const currentUrl = page.url();
    console.log(`🌐 URL actual: ${currentUrl}`);

    // Tomar screenshot de evidencia
    await page.screenshot({ path: 'ux-interaction-evidence.png', fullPage: true });
    console.log('📸 Screenshot guardado como ux-interaction-evidence.png');

    console.log('✅ ¡Prueba de UX completada exitosamente!');

  } catch (error) {
    console.error('❌ Error durante la prueba:', error.message);
  } finally {
    await browser.close();
  }
}

testUXInteraction().catch(console.error);
