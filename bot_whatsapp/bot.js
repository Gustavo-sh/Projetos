const qrcode = require('qrcode-terminal');
const { Client, LocalAuth } = require('whatsapp-web.js');

const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: {
        executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe'
    },
    puppeteerOptions: {
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    }
});

const express = require('express');
const app = express();

client.on('qr', qr => {
    qrcode.generate(qr, { small: true });
});

client.initialize();

app.use(express.json());

app.post('/send', async (req, res) => {

    try {

        const chat = await client.getChatById(
            req.body.group
        );

        await chat.sendMessage(
            req.body.message
        );

        res.send('ok');

    } catch (err) {

        console.error(err);

        res.status(500).send(err.message);

    }

});

app.listen(3000, () => {
    console.log('API iniciada');
});