import { MongoClient } from "mongodb";

const client = new MongoClient(process.env.MONGO_URI);

export default async function handler(req, res) {
    try {
        if (req.method !== "POST") {
            return res.status(405).json({ error: "Method not allowed" });
        }

        const { user_id, device_id } = req.body;

        if (!user_id || !device_id) {
            return res.json({ status: "error" });
        }

        await client.connect();
        const db = client.db("starbot");
        const users = db.collection("users");

        const ip =
            req.headers["x-forwarded-for"]?.split(",")[0] ||
            req.socket.remoteAddress;

        const deviceUser = await users.findOne({ device_id });
        if (deviceUser && deviceUser.user_id !== user_id) {
            return res.json({ status: "blocked_device" });
        }

        const ipCount = await users.countDocuments({ ip });
        if (ipCount >= 3) {
            return res.json({ status: "blocked_ip" });
        }

        const existing = await users.findOne({ user_id });
        if (existing && existing.verified) {
            return res.json({ status: "already" });
        }

        await users.updateOne(
            { user_id },
            {
                $set: {
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
        return res.json({ status: "error" });
    }
}
