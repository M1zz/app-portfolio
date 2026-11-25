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
  const label = event(type, notification.subtype);
  if (!label || !transaction) return null;

  const sandbox = notification.data.environment === 'Sandbox';
  const price = money(transaction.price, transaction.currency);
  const country = COUNTRY[transaction.storefront] || transaction.storefront || '';
  const icon = type === 'REFUND' ? '↩️' : '💰';
  const title = `${icon} ${appName(app.name)} · ${label}${sandbox ? ' (테스트)' : ''}`;
  const message = [productLabel(transaction.productId), price, country].filter(Boolean).join(' · ');

  return {
    recordType: 'Purchase',
    recordName: notification.notificationUUID,
    fields: {
      title: { value: title },
      message: { value: message },
      bundleID: { value: notification.data.bundleId },
      productID: { value: transaction.productId },
      kind: { value: type },
      subtype: { value: notification.subtype || '' },
      priceMilli: { value: transaction.price ?? 0 },
      currency: { value: transaction.currency || '' },
      storefront: { value: transaction.storefront || '' },
      sandbox: { value: sandbox ? 1 : 0 },
      transactionID: { value: transaction.transactionId || '' },
      occurredAt: { value: notification.signedDate || Date.now() },
    },
  };
}

module.exports = { describe, productLabel, appName };
