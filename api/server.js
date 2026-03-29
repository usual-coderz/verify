import { MongoClient } from "mongodb";

let cachedClient = null;
let cachedDb = null;

async function connectDB() {
    if (cachedDb) return cachedDb;

    if (!cachedClient) {
        cachedClient = new MongoClient(process.env.MONGO_URI, {
            maxPoolSize: 10,
            serverSelectionTimeoutMS: 5000
        });
        await cachedClient.connect();
    }

    cachedDb = cachedClient.db("starbot");
    return cachedDb;
}

export default async function handler(req, res) {
    if (req.method !== "POST") {
        return res.status(405).json({ status: "error" });
    }

    try {
        const { user_id, device_id } = req.body;

        if (!user_id || !device_id) {
            return res.json({ status: "error" });
        }

        const db = await connectDB();
        const users = db.collection("users");

        const ip =
            req.headers["x-forwarded-for"]?.split(",")[0]?.trim() ||
            req.socket?.remoteAddress ||
            "unknown";

        const existing = await users.findOne({ user_id });

        if (existing?.verified) {
            return res.json({ status: "already" });
        }

        const deviceUsed = await users.findOne({ device_id });

        if (deviceUsed && deviceUsed.user_id !== user_id) {
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
        console.error("❌ API ERROR:", err);
        return res.json({ status: "error" });
    }
}