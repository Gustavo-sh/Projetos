const express = require("express");
const pino = require("pino");
const qrcode = require("qrcode-terminal");

const {
    default: makeWASocket,
    DisconnectReason,
    useMultiFileAuthState,
    fetchLatestBaileysVersion
} = require("@whiskeysockets/baileys");

const app = express();

app.use(express.json());

let sock;

async function iniciarWhatsapp() {

    const { state, saveCreds } =
        await useMultiFileAuthState("./auth");

    const { version } =
        await fetchLatestBaileysVersion();

    sock = makeWASocket({
        version,
        auth: state,
        logger: pino({ level: "silent" })
    });

    sock.ev.on("creds.update", saveCreds);

    sock.ev.on("connection.update", (update) => {

        const { connection, qr, lastDisconnect } = update;

        if (qr) {
            qrcode.generate(qr, { small: true });
        }

        if (connection === "open") {
            console.log("WHATSAPP CONECTADO");
        }

        if (connection === "close") {

            const shouldReconnect =
                lastDisconnect?.error?.output?.statusCode !==
                DisconnectReason.loggedOut;

            if (shouldReconnect) {
                iniciarWhatsapp();
            }
        }
    });

    sock.ev.on("messages.upsert", async ({ messages }) => {

        const msg = messages[0];

        if (!msg.key.fromMe) {
            return;
        }

        if (!msg.message) {
            return;
        }

        const numero = msg.key.remoteJid;

        const texto =
            msg.message.conversation ||
            msg.message.extendedTextMessage?.text;

        console.log(numero);
        console.log(texto);

        if (texto === "ping") {

            await sock.sendMessage(numero, {
                text: "pong"
            });
        }
    });
}

app.post("/send", async (req, res) => {

    try {

        const destino = req.body.number;

        await sock.sendMessage(destino, {
            text: req.body.message
        });

        res.send("ok");

    } catch (erro) {

        console.error(erro);

        res.status(500).json({
            status: "erro",
            message: erro.message
        });
    }
});

app.listen(3000, () => {
    console.log("API iniciada");
});

iniciarWhatsapp();