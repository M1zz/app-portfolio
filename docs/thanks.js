/*
 * 고마운 사람들 — 앱 소개 페이지에 붙이는 공용 위젯.
 *
 * 소개 페이지에 이 두 줄을 넣는다:
 *   <section id="leeo-thanks" data-app="clip-keyboard" data-name="ClipKeyboard" data-mail="leeo@kakao.com"></section>
 *   <script src="https://m1zz.github.io/app-portfolio/thanks.js" defer></script>
 *
 * 이름은 같은 폴더의 thanks.json 에서 읽는다(앱 slug 별 목록). 페이지 언어(<html lang>)로 글을 고른다.
 * 이름이 아직 없어도 '이름 올리기' 안내는 보인다 — 응원한 사람이 여기 이름이 오른다는 걸 알 수 있게.
 */
(function () {
  var T = {
    ko: ["고마운 사람들", "이 앱을 응원해 주신 분들입니다. 덕분에 계속 만듭니다.", "첫 번째 이름을 기다리고 있어요.",
         "앱에서 응원해 주셨다면 이름을 여기에 올려 드려요. 올리고 싶은 이름과 App Store 영수증 메일의 주문 번호(Order ID)를 보내 주세요.", "이름 올리기", "고마운 사람들"],
    en: ["Thank you", "These people supported this app. Thanks to them, it keeps getting better.", "Waiting for the first name.",
         "If you tipped in the app, we'd love to list your name here. Send the name you'd like shown and the Order ID from your App Store receipt email.", "Add my name", "Thank-you list"],
    ja: ["ありがとう", "このアプリを応援してくださった方々です。おかげで作り続けられます。", "最初のお名前をお待ちしています。",
         "アプリで応援してくださった方のお名前をここに載せます。載せたいお名前と、App Store の領収書メールにある注文番号(Order ID)をお送りください。", "名前を載せる", "ありがとうリスト"],
    "zh-Hans": ["感谢名单", "这些朋友支持了这款应用。因为有你们，它才能继续变好。", "正在等待第一个名字。",
         "如果你在应用里打赏过，我们很乐意把你的名字列在这里。请发送想显示的名字，以及 App Store 收据邮件中的订单号（Order ID）。", "登上名单", "感谢名单"],
    "zh-Hant": ["感謝名單", "這些朋友支持了這款 App。因為有你們，它才能繼續變好。", "正在等待第一個名字。",
         "如果你在 App 裡贊助過，我們很樂意把你的名字列在這裡。請寄來想顯示的名字，以及 App Store 收據郵件中的訂單編號（Order ID）。", "登上名單", "感謝名單"],
    de: ["Danke", "Diese Menschen haben die App unterstützt. Dank ihnen geht es weiter.", "Wir warten auf den ersten Namen.",
         "Wenn du in der App Trinkgeld gegeben hast, nennen wir dich gern hier. Schick uns den gewünschten Namen und die Bestellnummer (Order ID) aus deiner App-Store-Quittung.", "Meinen Namen eintragen", "Dankesliste"],
    fr: ["Merci", "Ces personnes ont soutenu l'app. Grâce à elles, elle continue de s'améliorer.", "Nous attendons le premier nom.",
         "Si vous avez laissé un pourboire dans l'app, nous serons heureux d'afficher votre nom ici. Envoyez le nom souhaité et le numéro de commande (Order ID) de votre reçu App Store.", "Ajouter mon nom", "Liste de remerciements"],
    es: ["Gracias", "Estas personas apoyaron la app. Gracias a ellas, sigue mejorando.", "Esperando el primer nombre.",
         "Si diste una propina en la app, nos encantará poner tu nombre aquí. Envía el nombre que quieres mostrar y el número de pedido (Order ID) de tu recibo de App Store.", "Añadir mi nombre", "Lista de agradecimientos"],
    it: ["Grazie", "Queste persone hanno sostenuto l'app. Grazie a loro continua a migliorare.", "In attesa del primo nome.",
         "Se hai lasciato una mancia nell'app, saremo felici di mettere qui il tuo nome. Invia il nome da mostrare e il numero d'ordine (Order ID) della ricevuta App Store.", "Aggiungi il mio nome", "Lista dei ringraziamenti"],
    pt: ["Obrigado", "Estas pessoas apoiaram o app. Graças a elas, ele continua melhorando.", "Aguardando o primeiro nome.",
         "Se você deu uma gorjeta no app, vamos adorar colocar seu nome aqui. Envie o nome que deseja mostrar e o número do pedido (Order ID) do recibo da App Store.", "Incluir meu nome", "Lista de agradecimentos"],
    nl: ["Bedankt", "Deze mensen steunden de app. Dankzij hen wordt hij steeds beter.", "We wachten op de eerste naam.",
         "Heb je in de app een fooi gegeven? Dan zetten we je naam hier graag. Stuur de naam die je wilt tonen en het bestelnummer (Order ID) uit je App Store-bon.", "Mijn naam toevoegen", "Bedanklijst"],
    sv: ["Tack", "De här personerna har stöttat appen. Tack vare dem blir den bättre.", "Vi väntar på det första namnet.",
         "Om du har gett dricks i appen visar vi gärna ditt namn här. Skicka namnet du vill visa och ordernumret (Order ID) från ditt App Store-kvitto.", "Lägg till mitt namn", "Tacklista"],
    nb: ["Takk", "Disse menneskene har støttet appen. Takket være dem blir den bedre.", "Vi venter på det første navnet.",
         "Har du gitt tips i appen, viser vi gjerne navnet ditt her. Send navnet du vil vise og ordrenummeret (Order ID) fra App Store-kvitteringen.", "Legg til navnet mitt", "Takkeliste"],
    da: ["Tak", "Disse mennesker har støttet appen. Takket være dem bliver den bedre.", "Vi venter på det første navn.",
         "Har du givet drikkepenge i appen, viser vi gerne dit navn her. Send det navn, du vil vise, og ordrenummeret (Order ID) fra din App Store-kvittering.", "Tilføj mit navn", "Takkeliste"],
    fi: ["Kiitos", "Nämä ihmiset ovat tukeneet sovellusta. Heidän ansiostaan se paranee.", "Odotamme ensimmäistä nimeä.",
         "Jos annoit sovelluksessa tipin, lisäämme nimesi mielellämme tähän. Lähetä haluamasi nimi ja App Store -kuitin tilausnumero (Order ID).", "Lisää nimeni", "Kiitoslista"],
    pl: ["Dziękujemy", "Te osoby wsparły aplikację. Dzięki nim wciąż się rozwija.", "Czekamy na pierwsze imię.",
         "Jeśli dałeś napiwek w aplikacji, chętnie umieścimy tu Twoje imię. Wyślij imię do pokazania i numer zamówienia (Order ID) z rachunku App Store.", "Dodaj moje imię", "Lista podziękowań"],
    cs: ["Děkujeme", "Tito lidé aplikaci podpořili. Díky nim se dál zlepšuje.", "Čekáme na první jméno.",
         "Pokud jste v aplikaci dali spropitné, rádi tu uvedeme vaše jméno. Pošlete jméno, které chcete zobrazit, a číslo objednávky (Order ID) z účtenky App Store.", "Přidat mé jméno", "Seznam poděkování"],
    el: ["Ευχαριστούμε", "Αυτοί οι άνθρωποι στήριξαν την εφαρμογή. Χάρη σε αυτούς συνεχίζει να βελτιώνεται.", "Περιμένουμε το πρώτο όνομα.",
         "Αν αφήσατε φιλοδώρημα στην εφαρμογή, θα χαρούμε να γράψουμε το όνομά σας εδώ. Στείλτε το όνομα που θέλετε και τον αριθμό παραγγελίας (Order ID) από την απόδειξη του App Store.", "Προσθήκη του ονόματός μου", "Λίστα ευχαριστιών"],
    tr: ["Teşekkürler", "Bu kişiler uygulamayı destekledi. Onlar sayesinde gelişmeye devam ediyor.", "İlk ismi bekliyoruz.",
         "Uygulamada bahşiş verdiysen adını burada göstermekten mutluluk duyarız. Görünmesini istediğin adı ve App Store makbuzundaki sipariş numarasını (Order ID) gönder.", "Adımı ekle", "Teşekkür listesi"],
    ru: ["Спасибо", "Эти люди поддержали приложение. Благодаря им оно становится лучше.", "Ждём первое имя.",
         "Если вы оставили чаевые в приложении, мы с радостью укажем ваше имя здесь. Пришлите имя для показа и номер заказа (Order ID) из чека App Store.", "Добавить моё имя", "Список благодарностей"],
    id: ["Terima kasih", "Orang-orang ini mendukung aplikasi ini. Berkat mereka, aplikasi terus membaik.", "Menunggu nama pertama.",
         "Jika kamu memberi tip di aplikasi, kami senang mencantumkan namamu di sini. Kirim nama yang ingin ditampilkan dan nomor pesanan (Order ID) dari struk App Store.", "Cantumkan namaku", "Daftar terima kasih"],
    th: ["ขอบคุณ", "ผู้คนเหล่านี้สนับสนุนแอปนี้ แอปจึงพัฒนาต่อไปได้", "กำลังรอชื่อแรก",
         "ถ้าคุณเคยให้ทิปในแอป เรายินดีใส่ชื่อของคุณไว้ที่นี่ ส่งชื่อที่อยากให้แสดงและหมายเลขคำสั่งซื้อ (Order ID) จากใบเสร็จ App Store มาได้เลย", "ใส่ชื่อของฉัน", "รายชื่อขอบคุณ"],
    vi: ["Cảm ơn", "Những người này đã ủng hộ ứng dụng. Nhờ họ mà ứng dụng tiếp tục tốt hơn.", "Đang chờ cái tên đầu tiên.",
         "Nếu bạn đã gửi tiền tip trong ứng dụng, chúng tôi rất vui được ghi tên bạn ở đây. Hãy gửi tên muốn hiển thị và mã đơn hàng (Order ID) trong biên lai App Store.", "Ghi tên tôi", "Danh sách cảm ơn"]
  };

  function pick(lang) {
    lang = lang || "en";
    if (T[lang]) return T[lang];
    var l = lang.toLowerCase();
    if (l.indexOf("zh") === 0) return /hant|tw|hk|mo/.test(l) ? T["zh-Hant"] : T["zh-Hans"];
    if (l === "no" || l === "nn") return T.nb;
    return T[l.split("-")[0]] || T.en;
  }

  var CSS = "#leeo-thanks{max-width:760px;margin:56px auto;padding:0 20px;text-align:center;color:inherit;font:inherit;word-break:keep-all}" +
    "#leeo-thanks h2{font-size:1.5rem;margin:0 0 8px}" +
    "#leeo-thanks .lt-lead{margin:0 0 18px;opacity:.75;line-height:1.6}" +
    "#leeo-thanks ul{list-style:none;margin:0 0 18px;padding:0;display:flex;flex-wrap:wrap;gap:8px;justify-content:center}" +
    "#leeo-thanks li{padding:6px 14px;border-radius:999px;border:1px solid color-mix(in srgb,currentColor 22%,transparent);font-weight:600}" +
    "#leeo-thanks .lt-empty{opacity:.6;margin:0 0 18px}" +
    "#leeo-thanks .lt-how{font-size:1rem;opacity:.75;line-height:1.6;margin:0 0 12px}" +
    "#leeo-thanks .lt-cta{display:inline-block;padding:10px 20px;border-radius:999px;font-weight:700;text-decoration:none;" +
    "color:inherit;border:1.5px solid currentColor}";

  function render(box, names) {
    var t = pick(document.documentElement.getAttribute("lang"));
    var app = box.getAttribute("data-name") || document.title;
    var mail = box.getAttribute("data-mail") || "leeo@kakao.com";
    var html = "<h2>" + t[0] + "</h2><p class=\"lt-lead\">" + t[1] + "</p>";
    if (names.length) {
      html += "<ul>" + names.map(function (n) {
        var e = document.createElement("span");
        e.textContent = n.name;
        return "<li>" + e.innerHTML + "</li>";
      }).join("") + "</ul>";
    } else {
      html += "<p class=\"lt-empty\">" + t[2] + "</p>";
    }
    var subject = encodeURIComponent("[" + t[5] + "] " + app);
    html += "<p class=\"lt-how\">" + t[3] + "</p><a class=\"lt-cta\" href=\"mailto:" + mail + "?subject=" + subject + "\">" + t[4] + "</a>";
    box.innerHTML = html;
  }

  // defer 로 불러도 맨 위에서 실행되는 동안에는 currentScript 가 있다 — 콜백 안에서는 null 이라 여기서 잡아 둔다.
  var SRC = (document.currentScript && document.currentScript.src) || "https://m1zz.github.io/app-portfolio/thanks.js";

  function start() {
    var box = document.getElementById("leeo-thanks");
    if (!box) return;
    var style = document.createElement("style");
    style.textContent = CSS;
    document.head.appendChild(style);
    var names = [];
    render(box, names);
    // 언어를 페이지 안에서 바꾸는 소개 페이지(루트 index.html)는 <html lang> 이 바뀔 때 다시 그린다.
    new MutationObserver(function () { render(box, names); })
      .observe(document.documentElement, { attributes: true, attributeFilter: ["lang"] });
    fetch(SRC.replace(/thanks\.js(\?.*)?$/, "thanks.json"), { cache: "no-cache" })
      .then(function (r) { return r.ok ? r.json() : {}; })
      .then(function (d) {
        names = ((d.apps || {})[box.getAttribute("data-app")] || []).filter(function (n) { return n && n.name; });
        render(box, names);
      })
      .catch(function () {});
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
