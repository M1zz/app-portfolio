// Apple 의 소식 하나를 허브의 Purchase 레코드로 바꾼다. 돈이 움직이지 않은 소식은 null.
const COUNTRY = {
  KOR: '한국', USA: '미국', JPN: '일본', CHN: '중국', TWN: '대만', HKG: '홍콩', GBR: '영국',
  DEU: '독일', FRA: '프랑스', CAN: '캐나다', AUS: '호주', ESP: '스페인', ITA: '이탈리아',
  BRA: '브라질', MEX: '멕시코', IND: '인도', RUS: '러시아', VNM: '베트남', THA: '태국',
  IDN: '인도네시아', SGP: '싱가포르', NLD: '네덜란드', SWE: '스웨덴', CHE: '스위스', TUR: '튀르키예',
};

const PERIOD = { weekly: '주간', monthly: '월간', yearly: '연간', lifetime: '평생', upgrade: '업그레이드', graduate: '졸업' };

// "com.Ysoup.CoolTime.pro.yearly" → "Pro 연간", "…tip.small" → "팁 small"
function productLabel(productId) {
  const parts = productId.split('.');
  const [tier, kind] = parts.slice(-2);
  if (tier === 'tip') return `팁 ${kind}`;
  const t = tier.charAt(0).toUpperCase() + tier.slice(1);
  return `${t} ${PERIOD[kind] || kind}`;
}

function appName(name) {
  return name.split(/\s[-–:]\s|:\s/)[0].trim();
}

function money(milli, currency) {
  if (milli == null || !currency) return '';
  try {
    return new Intl.NumberFormat('ko-KR', { style: 'currency', currency }).format(milli / 1000);
  } catch {
    return `${milli / 1000} ${currency}`;
  }
}

function event(type, subtype) {
  switch (type) {
    case 'SUBSCRIBED': return subtype === 'RESUBSCRIBE' ? '다시 구독' : '새 구독';
    case 'DID_RENEW': return '구독 갱신';
    case 'ONE_TIME_CHARGE': return '구매';
    case 'OFFER_REDEEMED': return '할인 코드 구독';
    case 'REFUND': return '환불';
    default: return null;
  }
}

function describe(notification, transaction, app) {
  const type = notification.notificationType;
  const sandbox = notification.data.environment === 'Sandbox';

  // 허브 설정의 "시험 결제 알림 보내기" → Apple 의 TEST. 결제는 없지만 길 전체가 열렸는지 보인다.
  if (type === 'TEST') {
    return record(notification, {
      title: `🔔 ${appName(app.name)} · 결제 알림 시험`,
      message: 'Apple → 서버 → 허브 연결이 됩니다. 실제 결제는 아닙니다.',
      kind: type,
    });
  }

  const label = event(type, notification.subtype);
  if (!label || !transaction) return null;
  // 0원(오퍼 코드로 받은 평생 이용권 등)은 결제가 아니다 — 알리지 않는다. 판매 리포트에 "코드" 로 남는다.
  // 하루에 수십 건이 몰려 진짜 결제 알림을 덮는다(2026-11-26 인생 맛집 코드 20여 건).
  if (type !== 'REFUND' && !(transaction.price > 0)) return null;

  const price = money(transaction.price, transaction.currency);
  const country = COUNTRY[transaction.storefront] || transaction.storefront || '';
  const icon = type === 'REFUND' ? '↩️' : '💰';
  const title = `${icon} ${appName(app.name)} · ${label}${sandbox ? ' (테스트)' : ''}`;
  const message = [productLabel(transaction.productId), price, country].filter(Boolean).join(' · ');

  return record(notification, {
    title, message, kind: type,
    productID: transaction.productId,
    priceMilli: transaction.price ?? 0,
    currency: transaction.currency || '',
    storefront: transaction.storefront || '',
    transactionID: transaction.transactionId || '',
  });
}

function record(notification, f) {
  return {
    recordType: 'Purchase',
    recordName: notification.notificationUUID,
    fields: {
      title: { value: f.title },
      message: { value: f.message },
      bundleID: { value: notification.data.bundleId },
      productID: { value: f.productID || '' },
      kind: { value: f.kind },
      subtype: { value: notification.subtype || '' },
      priceMilli: { value: f.priceMilli || 0 },
      currency: { value: f.currency || '' },
      storefront: { value: f.storefront || '' },
      sandbox: { value: notification.data.environment === 'Sandbox' ? 1 : 0 },
      transactionID: { value: f.transactionID || '' },
      occurredAt: { value: notification.signedDate || Date.now() },
    },
  };
}

module.exports = { describe, productLabel, appName };
