import puppeteer from 'puppeteer-core';

(async () => {
  try {
    const browser = await puppeteer.launch({
      headless: 'new',
      executablePath: process.env.PUPPETEER_EXECUTABLE_PATH || '/usr/bin/google-chrome-stable',
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
    });
    const page = await browser.newPage();
    await page.goto('https://www.google.com');
    console.log('✅ Page loaded successfully');
    await browser.close();
  } catch (error) {
    console.error('❌ Error launching Puppeteer:', error);
    process.exit(1);
  }
})();
