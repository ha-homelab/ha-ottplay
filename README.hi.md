# Home Assistant के लिए OTTPlay

<!-- language-navigation:start -->
<p dir="ltr">
<a href="README.md" lang="en" dir="ltr">English</a> · <a href="README.ar.md" lang="ar" dir="rtl">العربية</a> · <a href="README.bn.md" lang="bn" dir="ltr">বাংলা</a> · <a href="README.cs.md" lang="cs" dir="ltr">Čeština</a> · <a href="README.de.md" lang="de" dir="ltr">Deutsch</a> · <a href="README.es.md" lang="es" dir="ltr">Español</a> · <a href="README.fa.md" lang="fa" dir="rtl">فارسی</a> · <a href="README.fr.md" lang="fr" dir="ltr">Français</a><br>
<a href="README.he.md" lang="he" dir="rtl">עברית</a> · <a href="README.hi.md" lang="hi" dir="ltr">हिन्दी</a> · <a href="README.id.md" lang="id" dir="ltr">Bahasa Indonesia</a> · <a href="README.it.md" lang="it" dir="ltr">Italiano</a> · <a href="README.ja.md" lang="ja" dir="ltr">日本語</a> · <a href="README.ko.md" lang="ko" dir="ltr">한국어</a> · <a href="README.nl.md" lang="nl" dir="ltr">Nederlands</a> · <a href="README.pl.md" lang="pl" dir="ltr">Polski</a><br>
<a href="README.pt.md" lang="pt" dir="ltr">Português</a> · <a href="README.ru.md" lang="ru" dir="ltr">Русский</a> · <a href="README.th.md" lang="th" dir="ltr">ไทย</a> · <a href="README.tr.md" lang="tr" dir="ltr">Türkçe</a> · <a href="README.uk.md" lang="uk" dir="ltr">Українська</a> · <a href="README.vi.md" lang="vi" dir="ltr">Tiếng Việt</a> · <a href="README.zh-Hans.md" lang="zh-Hans" dir="ltr">简体中文</a> · <a href="README.zh-Hant.md" lang="zh-Hant" dir="ltr">繁體中文</a>
</p>
<!-- language-navigation:end -->

[![RC fuzzing](https://img.shields.io/badge/fuzzing-RC_only-0a9f8f)](docs/fuzzing.md)

[आर्किटेक्चर](docs/architecture.md) · [सुरक्षा](SECURITY.md) · [योगदान](CONTRIBUTING.md)

अपने मौजूदा [OTTPlay Control Server](https://github.com/open-ott-play/ottplay-control-server) के ज़रिए Home Assistant से पंजीकृत OTTPlay प्लेयर नियंत्रित करें। एक कनेक्शन हर प्लेयर को एक `media_player` एंटिटी और एक `remote` एंटिटी देता है। टीवी नियंत्रक को बाहर की ओर अनुरोध भेजता है; Home Assistant के लिए टीवी पर सुनने वाला पोर्ट, MQTT ब्रोकर या दूसरा ब्रिज प्रोसेस आवश्यक नहीं है।

![यह कैसे काम करता है](docs/diagrams/architecture.svg)

## उपलब्ध सुविधाएँ

- चालू प्लेयर से पढ़ी गई प्लेबैक स्थिति, जिसमें अनुपलब्ध डिवाइस स्पष्ट रूप से चिह्नित होते हैं।
- प्लेयर के समर्थन के अनुसार चलाना/रोककर रखना, पिछला/अगला चैनल, प्लेबैक स्थिति बदलना और आवाज़ का स्तर।
- `media_player.play_media` के ज़रिए नंबर या नाम से चैनल चुनना।
- `remote.send_command` के ज़रिए नेविगेशन: तीर, OK, वापस और अन्य समर्थित कुंजियाँ।
- UI से कॉन्फ़िगरेशन, क्रेडेंशियल बदलना, अंग्रेज़ी/रूसी इंटरफ़ेस अनुवाद और संवेदनशील जानकारी छिपाए गए डायग्नोस्टिक्स।
- प्लेयर दोबारा शुरू होने पर भी स्थिर एंटिटी पहचान।

क्षमताएँ प्लेयर के बिल्ड, प्लेबैक मोड और कनेक्शन पर निर्भर करती हैं। स्टॉप और हार्डवेयर पावर बटन उपलब्ध नहीं कराए जाते: स्टैंडबाय/जगाने का अर्थ हर प्लेयर में अलग हो सकता है और उन्हें प्लेबैक बंद करने/फिर शुरू करने के विकल्प के रूप में इस्तेमाल नहीं किया जाता। इंटीग्रेशन मौजूदा शीर्षक, चित्र या हार्डवेयर की पावर स्थिति गढ़ता नहीं है। नियंत्रक की पुष्टि का अर्थ है कि हैंडलर ने जवाब दिया; इससे यह साबित नहीं होता कि चित्र दिख रहा है या आवाज़ सुनाई दे रही है। स्थिति बाद में किए गए रीड से मिलती है।

## इंस्टॉल करना

**Home Assistant 2026.10.0 या नया** और अनुरोध/प्रतिक्रिया API का समर्थन करने वाले मौजूदा OTTPlay Control Server तथा प्लेयर की आवश्यकता है। यह एक कस्टम इंटीग्रेशन है, Home Assistant Core का हिस्सा या HACS की डिफ़ॉल्ट रिपॉज़िटरी नहीं है।

**HACS:** `ha-homelab/ha-ottplay` को **Integration** प्रकार की कस्टम रिपॉज़िटरी के रूप में जोड़ें, **OTTPlay** इंस्टॉल करें और Home Assistant दोबारा शुरू करें। बीटा इंस्टॉल करते समय HACS में प्रीरिलीज़ सक्षम करें।

**मैन्युअल:** [रिलीज़](https://github.com/ha-homelab/ha-ottplay/releases) से `ha-ottplay.zip` डाउनलोड करें, उसका चेकसम जाँचें और उसके `custom_components/ottplay` फ़ोल्डर को अपने HA कॉन्फ़िगरेशन फ़ोल्डर में निकालें। मौजूदा HA फ़ाइलें बनाए रखें। Home Assistant दोबारा शुरू करें।

**सेटिंग्स → डिवाइस और सेवाएँ → इंटीग्रेशन जोड़ें → OTTPlay** पर जाएँ। ऐसा URL इस्तेमाल करें जिस तक Home Assistant स्वयं पहुँच सकता हो, और नियंत्रक के पथ का कोई प्रीफ़िक्स हो तो उसे भी शामिल करें। उदाहरण: `https://controller.example.net/ott-control`।

दो प्राधिकरण मोड समर्थित हैं:

1. **सीमित ऑपरेटर (अनुशंसित):** अलग कमांड-ऑपरेटर टोकन इस्तेमाल करें और कॉन्फ़िगरेशन फ़ॉर्म में उसके अनुमत प्लेयर ID लिखें। ID पाने के लिए `ott devices` इस्तेमाल करें। नया प्लेयर पंजीकृत करने से यह अनुमति अपने-आप नहीं बढ़ती; सर्वर की अनुमति और इंटीग्रेशन कॉन्फ़िगरेशन सोच-समझकर अपडेट करें।
2. **स्वचालित रजिस्ट्री:** प्लेयर ID खाली छोड़ें और सर्वर एडमिनिस्ट्रेटर टोकन इस्तेमाल करें। इंटीग्रेशन सर्वर रजिस्ट्री पढ़कर नए डिवाइस खोजता है। यह क्रेडेंशियल बहुत अधिक व्यापक पहुँच देता है। इसका उपयोग केवल भरोसेमंद HA इंस्टेंस के साथ करें।

डिवाइस टोकन और केवल डायग्नोस्टिक्स वाले ऑपरेटर टोकन यहाँ इस्तेमाल नहीं किए जा सकते। [कॉन्फ़िगरेशन और अनुमतियाँ](docs/configuration.md) देखें।

## ऑटोमेशन में उपयोग

```yaml
action: media_player.play_media
target:
  entity_id: media_player.ottplay_living_room
data:
  media_content_type: channel
  media_content_id: "12"
```

```yaml
action: remote.send_command
target:
  entity_id: remote.ottplay_living_room
data:
  command: [ok, down, back]
```

उदाहरण के एंटिटी ID को अपने सिस्टम में बने ID से बदलें। चैनल चयन प्लेयर के मौजूदा प्रदाता का इस्तेमाल करता है; यह कोई भी मनमाना मीडिया URL अपलोड नहीं करता। कॉन्फ़िगरेशन प्लेबैक शुरू नहीं करता और न ही टीवी की भौतिक पावर नियंत्रित करता है।

## विकास और रिलीज़

Python 3.14 इस्तेमाल करें और `uv sync --locked` चलाएँ, फिर `uv run pytest -q`, `uv run ruff check .` और `uv run ruff format --check .` चलाएँ। परीक्षण घरेलू डिवाइस से जुड़े बिना प्रोटोकॉल की विफलताओं, क्रेडेंशियल, जीवनचक्र और वास्तविक HA एंटिटी सेवाओं की जाँच करते हैं। [रिलीज़ प्रक्रिया](docs/releasing.md) देखें।

सार्वजनिक रिपॉज़िटरी की सेटिंग्स [Terraform](https://github.com/4alvit/terraform-github-ha-homelab) से प्रबंधित होती हैं। CI, [venus-os-ci-toolkit](https://github.com/victron-venus/venus-os-ci-toolkit) के निश्चित रिविज़न पर पिन किए गए साझा वर्कफ़्लो इस्तेमाल करता है।
