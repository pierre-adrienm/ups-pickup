const puppeteer = require('puppeteer-extra');
const fs = require('fs');
require('dotenv').config({ path: '/app/.env' });

const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin());

(async () => {
  console.log('🔍 UPS_ACCOUNT_NUMBER =', process.env.UPS_ACCOUNT_NUMBER);

  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();

  await page.setUserAgent(
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' +
    '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  );

  try {
    // 1. Aller sur la page d'accueil UPS
    await page.goto('https://id.ups.com', {
      waitUntil: 'networkidle2',
      timeout: 90000
    });
    console.log('✅ Page chargée avec succès.');

    // 2. Cliquer sur "Log In"
    await page.waitForSelector('#anonymous-profile', { visible: true });
    await page.click('#anonymous-profile');
    console.log('👉 Bouton "Log In" cliqué');
    await new Promise(resolve => setTimeout(resolve, 1500));

    // 3. Remplir l'identifiant
    await page.waitForSelector('input#username', { visible: true });
    await page.type('#username', process.env.UPS_ACCOUNT_NUMBER, { delay: 100 });
    console.log('⌨️ Champ "username" rempli');
    await page.click('button[type="submit"]');
    await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 60000 });

    // 4. Remplir le mot de passe
    await page.waitForSelector('input#password', { visible: true });
    await page.type('#password', process.env.UPS_ACCOUNT_PASSWORD, { delay: 100 });
    console.log('🔑 Champ "password" rempli');
    await page.click('button._button-login-password');
    await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 60000 });
    console.log('✅ Connexion réussie');

    // 5. Fermer une éventuelle modale
    try {
      await page.waitForSelector('button[aria-label="Close"]', { timeout: 5000 });
      await page.click('button[aria-label="Close"]');
      console.log('❎ Fenêtre modale fermée');
    } catch {
      console.log('ℹ️ Aucune fenêtre modale détectée');
    }

    // 6. Aller manuellement à la page "Schedule a Pickup"
    try {
      const pickupUrl = 'https://wwwapps.ups.com/pickup/schedule?loc=fr_FR';
      console.log(`🚀 Navigation manuelle vers ${pickupUrl}`);
      await page.goto(pickupUrl, { waitUntil: 'networkidle2', timeout: 90000 });

      await page.waitForSelector('form[name="PickupScheduleForm"], h1', { timeout: 10000 }).catch(() => {
        console.log('⏳ Aucun sélecteur distinctif détecté sur la page de pickup');
      });

      const html = await page.content();
      fs.writeFileSync('/data/ups_pickup_schedule.html', html);
      await page.screenshot({ path: '/data/ups_pickup_schedule.png', fullPage: true });
      console.log('📸 Capture "Schedule a Pickup" enregistrée');
    } catch (err) {
      console.log('⚠️ Erreur lors de la navigation vers "Schedule a Pickup"', err);
    }

  } catch (err) {
    console.error('❌ Erreur :', err);
  }

  await browser.close();
})();
