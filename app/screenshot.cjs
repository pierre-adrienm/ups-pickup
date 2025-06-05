const puppeteer = require('puppeteer-extra');
const fs = require('fs');
require('dotenv').config({ path: '/app/.env' });
const fetch = require('node-fetch');

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
    // 1. Accueil UPS
    await page.goto('https://id.ups.com', {
      waitUntil: 'networkidle2',
      timeout: 90000
    });
    console.log('✅ Page chargée avec succès.');

    // 2. Log In
    await page.waitForSelector('#anonymous-profile', { visible: true });
    await page.click('#anonymous-profile');
    console.log('👉 Bouton "Log In" cliqué');
    await new Promise(resolve => setTimeout(resolve, 1500));

    // 3. Username
    await page.waitForSelector('input#username', { visible: true });
    await page.type('#username', process.env.UPS_ACCOUNT_NUMBER, { delay: 100 });
    console.log('⌨️ Champ "username" rempli');
    await page.click('button[type="submit"]');

    // 4. Gestion cookie après "submit"
    try {
      await page.waitForSelector('button#preferences_prompt_submit', { visible: true, timeout: 10000 });
      await Promise.all([
        page.click('button#preferences_prompt_submit'),
        page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 15000 }).catch(() => {})
      ]);
      console.log('🍪 Bouton cookie "Confirmer" cliqué');

      // 🔁 Saisie du nom à nouveau car le formulaire a été réinitialisé
      await page.waitForSelector('input#username', { visible: true });
      await page.type('#username', process.env.UPS_ACCOUNT_NUMBER, { delay: 100 });
      console.log('⌨️ Champ "username" ressaisi après cookies');
      await page.click('button[type="submit"]');

    } catch {
      console.log('ℹ️ Aucun bandeau cookies détecté après username');
    }

    // 5. Attente champ mot de passe
    try {
      await page.waitForSelector('input#password', { visible: true, timeout: 30000 });
      console.log('👀 Champ "password" détecté');
    } catch (err) {
      console.error('❌ Champ "password" non détecté après username + cookies');
      const html = await page.content();
      fs.writeFileSync('/data/ups_after_username_submit.html', html);
      await page.screenshot({ path: '/data/ups_after_username_submit.png', fullPage: true });
      throw err;
    }

    // 6. Mot de passe
    await page.type('#password', process.env.UPS_ACCOUNT_PASSWORD, { delay: 100 });
    console.log('🔑 Champ "password" rempli');

    await Promise.all([
      page.click('button._button-login-password'),
      page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 60000 })
    ]);
    console.log('✅ Connexion réussie');

    // 7. Fermer modale si présente
    try {
      await page.waitForSelector('button[aria-label="Close"]', { timeout: 5000 });
      await page.click('button[aria-label="Close"]');
      console.log('❎ Fenêtre modale fermée');
    } catch {
      console.log('ℹ️ Aucune fenêtre modale détectée');
    }

    // 8. Accès à l’historique
    const pickupUrl = 'https://wwwapps.ups.com/pickup/history?loc=fr_FR';
    console.log(`🚀 Navigation vers ${pickupUrl}`);
    await page.goto(pickupUrl, { waitUntil: 'networkidle2', timeout: 90000 });

    await page.waitForSelector('form[name="PickuphistoryForm"], h1', { timeout: 10000 }).catch(() => {
      console.log('⏳ Aucun sélecteur distinctif détecté sur la page de pickup');
    });

    const htmlContent = await page.content();
    
    // Charger le HTML sauvegardé
    fs.writeFileSync('/data/ups_pickup_history.html', htmlContent, 'utf-8');
    await page.screenshot({ path: '/data/ups_pickup_history.png', fullPage: true });
    console.log('📸 HTML et capture écran sauvegardés');

    const cheerio = require('cheerio');
    const $ = cheerio.load(htmlContent);

    // Extraire les données du tableau
    const data = [];
    $('table.dataTable.borderWhite tbody tr').each((_, tr) => {
      const tds = $(tr).find('td');
      if (tds.length >= 6) {
        const row = {
          date: $(tds[1]).text().trim(),
          orderNumber: $(tds[2]).text().trim(),
          contactName: $(tds[3]).text().trim(),
          reference: $(tds[4]).text().trim(),
          status: $(tds[5]).text().trim()
        };
        data.push(row);
      }
    });

    // Sauvegarder dans un fichier JSON
    fs.writeFileSync('/data/last_pickup.json', JSON.stringify(data, null, 2), 'utf-8');
    console.log('✅ Données du tableau enregistrées dans last_pickup.json');
    
    const webhookUrl = 'https://hook.eu2.make.com/tgxqrx7tqpf8358644fp91xustsdiyeh';

    if (data.length > 0) {
      const firstRow = data[0];
      console.log('🧪 Envoi de la première ligne à Make :', firstRow);

      const response = await fetch(webhookUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(firstRow)
      });

      console.log('📤 Première ligne envoyée à Make. Statut :', response.status);
    }

  } catch (err) {
    console.error('❌ Erreur générale :', err);
  }

  await browser.close();
})();
