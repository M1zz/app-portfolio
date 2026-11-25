// CloudKit Web Services — 서버 키로 허브 공개 데이터베이스에 쓴다.
// 서명: base64(ECDSA-SHA256("날짜:base64(sha256(본문)):하위경로"))
const crypto = require('crypto');

const CONTAINER = 'iCloud.com.Ysoup.FeedbackHub';

async function ck(env, op, body) {
  const keyId = process.env.CK_KEY_ID;
  const privateKey = process.env.CK_PRIVATE_KEY.replace(/\\n/g, '\n');
  const subpath = `/database/1/${CONTAINER}/${env}/public/${op}`;
  const json = JSON.stringify(body);
  const date = new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');
  const bodyHash = crypto.createHash('sha256').update(json).digest('base64');
  const signature = crypto.sign('sha256', Buffer.from(`${date}:${bodyHash}:${subpath}`), privateKey).toString('base64');
  const res = await fetch(`https://api.apple-cloudkit.com${subpath}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Apple-CloudKit-Request-KeyID': keyId,
      'X-Apple-CloudKit-Request-ISO8601Date': date,
      'X-Apple-CloudKit-Request-SignatureV1': signature,
    },
    body: json,
  });
  const out = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(`CloudKit ${res.status}: ${JSON.stringify(out)}`);
  return out;
}

module.exports = { ck };
