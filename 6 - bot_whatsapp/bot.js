console.log('SCRIPT INICIADO');
const qrcode = require('qrcode-terminal');
const { Client, LocalAuth } = require('whatsapp-web.js');

// const client = new Client({
//     authStrategy: new LocalAuth(),
//     puppeteer: {
//         executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe'
//     },
//     puppeteerOptions: {
//         args: ['--no-sandbox', '--disable-setuid-sandbox']
//     }
// });

const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: {
        executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
        headless: false
    },
});

const express = require('express');
const app = express();

client.on('qr', qr => {
    qrcode.generate(qr, { small: true });
});

client.on("ready", async () => {

    console.log("WHATSAPP PRONTO");

    const page = client.pupPage;

    try {

        const titulo = await page.title();
        console.log("Título:", titulo);

        const estado = await page.evaluate(() => ({
            location: location.href,
            documentReady: document.readyState,
            hasStore: typeof window.Store,
            hasWWebJS: typeof window.WWebJS
        }));

        console.log(estado);



        console.log(
            "WhatsApp Web:",
            await client.getWWebVersion()
        );

        const page = client.pupPage;

        const result = await page.evaluate(() => ({
            Store: typeof window.Store,
            WWebJS: typeof window.WWebJS,
            webpack: Object.keys(window).filter(k => k.startsWith("webpack")),
            keys: Object.keys(window).filter(k => k.toLowerCase().includes("store"))
        }));

        console.log(result);

    } catch(e) {

        console.error("Evaluate manual:");
        console.error(e);

    }

});


client.on("loading_screen", (percent, message) => {
    console.log(percent, message);
});

client.on("authenticated", () => {
    console.log("AUTHENTICATED");
});

client.on("auth_failure", msg => {
    console.error("AUTH FAILURE:", msg);
});

client.on("disconnected", reason => {
    console.error("DISCONNECTED:", reason);
});

client.on("change_state", state => {
    console.log("STATE:", state);
});

client.on("remote_session_saved", () => {
    console.log("REMOTE SESSION SAVED");
});

client.initialize();

app.use(express.json());

app.post('/send', async (req, res) => {

    try {

        console.log(req.body.group);

        const chats = await client.getChats();

        console.log("Chats carregados:", chats.length);

        const chat = chats.find(
            c => c.id._serialized === req.body.group
        );

        console.log(chat);

        if (!chat) {
            throw new Error("Grupo não encontrado");
        }

        await chat.sendMessage(req.body.message);
        res.send('ok');

    } catch (err) {
        console.error(err);
        console.error(err.stack);

        if (err.originalError) {
            console.error(err.originalError);
        }

        res.status(500).send(err.message);
    }
    });

app.listen(3000, () => {
    console.log('API iniciada');
});