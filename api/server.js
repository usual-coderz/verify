import { MongoClient } from "mongodb";

let client;
let db;

async function connectDB() {
    if (!client) {
        client = new MongoClient(process.env.MONGO_URI, {
            maxPoolSize: 10
        });
        await client.connect();
        db = client.db("starbot");
    }
    return db;
}

export default async function handler(req, res) {
    try {
        if (req.method !== "POST") {
            return res.status(405).json({ status: "error" });
        }

        const { user_id, device_id } = req.body;

        if (!user_id || !device_id) {
            return res.json({ status: "error" });
        }

        const database = await connectDB();
        const users = database.collection("users");

        const ip =
            req.headers["x-forwarded-for"]?.split(",")[0] ||
            req.socket.remoteAddress ||
            "unknown";

        const existingUser = await users.findOne({ user_id });

        if (existingUser && existingUser.verified) {
            return res.json({ status: "already" });
        }

        const deviceCheck = await users.findOne({ device_id });
        if (deviceCheck && deviceCheck.user_id !== user_id) {
            return res.json({ status: "blocked_device" });
        }

        const ipCount = await users.countDocuments({ ip });
        if (ipCount >= 3) {
            return res.json({ status: "blocked_ip" });
        }

        await users.updateOne(
            { user_id },
            {
                $set: {
                    user_id,
                    device_id,
                    ip,
                    verified: true,
                    verified_at: new Date()
                }
            },
            { upsert: true }
        );

        return res.json({ status: "ok" });

    } catch (err) {
        console.error("ERROR:", err);
        return res.json({ status: "error" });
    }
}