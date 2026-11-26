// Apple 이 결제 소식을 보내는 곳 (App Store Server Notifications V2).
//
// 1. 서명을 Apple 루트 인증서까지 따라가 확인한다 — 아무나 이 주소로 가짜 결제를 못 넣는다.
// 2. 돈이 움직인 소식(첫 구매 · 갱신 · 일회성 구매 · 환불)만 허브 CloudKit 에 Purchase 로 남긴다.
// 3. 허브 앱이 Purchase 생성을 구독하고 있어서 아이폰 · 맥에 바로 푸시가 뜬다.
//
// 레코드 이름은 Apple 의 notificationUUID 라서, Apple 이 다시 보내도 두 번 울리지 않는다.
const fs = require('fs');
const path = require('path');
const { SignedDataVerifier, Environment } = require('@apple/app-store-server-library');
const { ck } = require('../lib/cloudkit');
const { describe } = require('../lib/describe');

const APPS = require('../lib/apps.json');
const ROOTS = [fs.readFileSync(path.join(__dirname, '../lib/AppleRootCA-G3.cer'))];

function peek(jws) {
  return JSON.parse(Buffer.from(jws.split('.')[1], 'base64url').toString('utf8'));
}

async function verify(signedPayload) {
  // 어느 앱 · 어느 환경인지는 서명 확인 전에 알아야 확인기를 만들 수 있다. 확인은 그다음에 한다.
  const claimed = peek(signedPayload).data || {};
  const app = APPS[claimed.bundleId];
  if (!app) throw new Error(`모르는 앱: ${claimed.bundleId}`);
  const env = claimed.environment === 'Sandbox' ? Environment.SANDBOX : Environment.PRODUCTION;
  const verifier = new SignedDataVerifier(ROOTS, true, env, claimed.bundleId, Number(app.id));
  const notification = await verifier.verifyAndDecodeNotification(signedPayload);
  const transaction = notification.data?.signedTransactionInfo
    ? await verifier.verifyAndDecodeTransaction(notification.data.signedTransactionInfo)
    : null;
  return { notification, transaction, app };
}

module.exports = async (req, res) => {
  if (req.method !== 'POST') return res.status(405).end();
  let verified;
  try {
    verified = await verify(req.body?.signedPayload || '');
  } catch (e) {
    console.error('❌ 서명 확인 실패', e.message);
    // 4xx 면 Apple 이 다시 보내지 않는다. 가짜나 모르는 앱은 다시 받을 이유가 없다.
    return res.status(400).json({ error: 'unverified' });
  }
  const { notification, transaction, app } = verified;
  // 샌드박스(시험 결제 · 연결 시험)는 남기지 않는다. 시험 구독은 몇 분마다 갱신돼 알림이 쏟아졌다(2026-11-26).
  if (notification.data?.environment === 'Sandbox') return res.status(200).json({ skipped: 'sandbox' });
  const record = describe(notification, transaction, app);
  if (!record) return res.status(200).json({ skipped: notification.notificationType });

  try {
    await ck(process.env.CK_ENVIRONMENT || 'production', 'records/modify', {
      operations: [{ operationType: 'forceReplace', record }],
    });
  } catch (e) {
    console.error('❌ CloudKit 기록 실패', e.message);
    // 5xx 면 Apple 이 시간을 두고 다시 보낸다.
    return res.status(500).json({ error: 'store' });
  }
  console.log('✅', record.fields.title.value, record.fields.message.value);
  res.status(200).json({ ok: true });
};
