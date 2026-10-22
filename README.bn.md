# Home Assistant-এর জন্য OTTPlay

<!-- language-navigation:start -->
<p dir="ltr">
<a href="README.md" lang="en" dir="ltr">English</a> · <a href="README.ar.md" lang="ar" dir="rtl">العربية</a> · <a href="README.bn.md" lang="bn" dir="ltr">বাংলা</a> · <a href="README.cs.md" lang="cs" dir="ltr">Čeština</a> · <a href="README.de.md" lang="de" dir="ltr">Deutsch</a> · <a href="README.es.md" lang="es" dir="ltr">Español</a> · <a href="README.fa.md" lang="fa" dir="rtl">فارسی</a> · <a href="README.fr.md" lang="fr" dir="ltr">Français</a><br>
<a href="README.he.md" lang="he" dir="rtl">עברית</a> · <a href="README.hi.md" lang="hi" dir="ltr">हिन्दी</a> · <a href="README.id.md" lang="id" dir="ltr">Bahasa Indonesia</a> · <a href="README.it.md" lang="it" dir="ltr">Italiano</a> · <a href="README.ja.md" lang="ja" dir="ltr">日本語</a> · <a href="README.ko.md" lang="ko" dir="ltr">한국어</a> · <a href="README.nl.md" lang="nl" dir="ltr">Nederlands</a> · <a href="README.pl.md" lang="pl" dir="ltr">Polski</a><br>
<a href="README.pt.md" lang="pt" dir="ltr">Português</a> · <a href="README.ru.md" lang="ru" dir="ltr">Русский</a> · <a href="README.th.md" lang="th" dir="ltr">ไทย</a> · <a href="README.tr.md" lang="tr" dir="ltr">Türkçe</a> · <a href="README.uk.md" lang="uk" dir="ltr">Українська</a> · <a href="README.vi.md" lang="vi" dir="ltr">Tiếng Việt</a> · <a href="README.zh-Hans.md" lang="zh-Hans" dir="ltr">简体中文</a> · <a href="README.zh-Hant.md" lang="zh-Hant" dir="ltr">繁體中文</a>
</p>
<!-- language-navigation:end -->

[![RC fuzzing](https://img.shields.io/badge/fuzzing-RC_only-0a9f8f)](docs/fuzzing.md)

[স্থাপত্য](docs/architecture.md) · [নিরাপত্তা](SECURITY.md) · [অবদান রাখা](CONTRIBUTING.md)

আপনার বিদ্যমান [OTTPlay Control Server](https://github.com/open-ott-play/ottplay-control-server) ব্যবহার করে Home Assistant থেকে নিবন্ধিত OTTPlay প্লেয়ার নিয়ন্ত্রণ করুন। একটি সংযোগ প্রতিটি প্লেয়ারের জন্য একটি `media_player` এনটিটি ও একটি `remote` এনটিটি দেয়। টিভি নিয়ন্ত্রকের কাছে বহির্গামী অনুরোধ পাঠায়; Home Assistant-এর জন্য টিভিতে সংযোগ গ্রহণকারী পোর্ট, MQTT ব্রোকার বা দ্বিতীয় ব্রিজ প্রক্রিয়া প্রয়োজন হয় না।

![যেভাবে কাজ করে](docs/diagrams/architecture.svg)

## যা পাবেন

- চলমান প্লেয়ার থেকে পড়া প্লেব্যাকের অবস্থা, যেখানে অনুপলব্ধ ডিভাইস স্পষ্টভাবে চিহ্নিত থাকে।
- প্লেয়ার সমর্থন করলে চালানো/বিরতি, আগের/পরের চ্যানেল, প্লেব্যাকের অবস্থান পরিবর্তন এবং ভলিউম নিয়ন্ত্রণ।
- `media_player.play_media` দিয়ে নম্বর বা নাম অনুসারে চ্যানেল নির্বাচন।
- `remote.send_command` দিয়ে নেভিগেশন: তীরচিহ্ন, OK, ফিরে যাওয়া এবং অন্যান্য সমর্থিত কী।
- UI দিয়ে কনফিগারেশন, পরিচয় যাচাইয়ের তথ্য বদলানো, ইংরেজি/রুশ ইন্টারফেস অনুবাদ এবং সংবেদনশীল তথ্য আড়াল করা ডায়াগনস্টিকস।
- প্লেয়ার পুনরায় চালু হলেও এনটিটির স্থায়ী পরিচয়।

সক্ষমতা প্লেয়ারের বিল্ড, প্লেব্যাক মোড ও সংযোগের ওপর নির্ভর করে। থামানো ও হার্ডওয়্যার পাওয়ার বোতাম দেওয়া হয় না: স্ট্যান্ডবাই/জাগানোর অর্থ একেক প্লেয়ারে একেক রকম হতে পারে এবং এগুলো প্লেব্যাক থামানো/আবার চালানোর বিকল্প নয়। ইন্টিগ্রেশন বর্তমান শিরোনাম, ছবি বা হার্ডওয়্যারের পাওয়ার অবস্থা বানিয়ে দেখায় না। নিয়ন্ত্রকের স্বীকৃতির অর্থ হ্যান্ডলার উত্তর দিয়েছে; এটি প্রমাণ করে না যে ছবি দেখা যাচ্ছে বা শব্দ শোনা যাচ্ছে। পরবর্তী পাঠ থেকে অবস্থা পাওয়া যায়।

## ইনস্টল

প্রয়োজন **Home Assistant 2026.10.0 বা পরবর্তী সংস্করণ**, সঙ্গে অনুরোধ/উত্তর API সমর্থনকারী বর্তমান OTTPlay Control Server ও প্লেয়ার। এটি কাস্টম ইন্টিগ্রেশন; Home Assistant Core-এর অংশ বা HACS-এর ডিফল্ট রিপোজিটরি নয়।

**HACS:** `ha-homelab/ha-ottplay`-কে **Integration** ধরনের কাস্টম রিপোজিটরি হিসেবে যোগ করুন, **OTTPlay** ইনস্টল করুন, তারপর Home Assistant পুনরায় চালু করুন। বিটা ইনস্টল করার সময় HACS-এ প্রিরিলিজ সক্রিয় করুন।

**ম্যানুয়াল:** [রিলিজ](https://github.com/ha-homelab/ha-ottplay/releases) থেকে `ha-ottplay.zip` ডাউনলোড করুন, এর চেকসাম যাচাই করুন এবং ভেতরের `custom_components/ottplay` ডিরেক্টরি আপনার HA কনফিগারেশন ডিরেক্টরিতে আনজিপ করুন। বিদ্যমান HA ফাইলগুলো রাখুন। Home Assistant পুনরায় চালু করুন।

**সেটিংস → ডিভাইস ও পরিষেবা → ইন্টিগ্রেশন যোগ করুন → OTTPlay**-এ যান। এমন URL ব্যবহার করুন যেখানে Home Assistant নিজে পৌঁছাতে পারে; নিয়ন্ত্রকের পাথের কোনো প্রিফিক্স থাকলে সেটিও রাখুন। উদাহরণ: `https://controller.example.net/ott-control`।

দুটি অনুমোদন মোড সমর্থিত:

1. **সীমিত অপারেটর (প্রস্তাবিত):** নির্দিষ্ট কমান্ড-অপারেটর টোকেন ব্যবহার করুন এবং কনফিগারেশন ফর্মে তার অনুমোদিত প্লেয়ার ID লিখুন। `ott devices` থেকে ID সংগ্রহ করুন। নতুন প্লেয়ার নিবন্ধন করলে এই অনুমতি আপনাআপনি বাড়ে না; সচেতনভাবে সার্ভারের অনুমতি ও ইন্টিগ্রেশনের কনফিগারেশন হালনাগাদ করুন।
2. **স্বয়ংক্রিয় রেজিস্ট্রি:** প্লেয়ার ID খালি রাখুন এবং সার্ভার প্রশাসকের টোকেন ব্যবহার করুন। ইন্টিগ্রেশন সার্ভারের রেজিস্ট্রি পড়ে নতুন ডিভাইস খুঁজে পায়। এই পরিচয় যাচাইয়ের তথ্য অনেক বেশি বিস্তৃত প্রবেশাধিকার দেয়। কেবল বিশ্বস্ত HA ইনস্ট্যান্সের সঙ্গে ব্যবহার করুন।

ডিভাইস টোকেন বা শুধু ডায়াগনস্টিকসের জন্য নির্ধারিত অপারেটর টোকেন এখানে ব্যবহার করা যায় না। [কনফিগারেশন ও অনুমতি](docs/configuration.md) দেখুন।

## অটোমেশনে ব্যবহার

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

উদাহরণের এনটিটি ID আপনার সিস্টেমে তৈরি হওয়া ID দিয়ে বদলান। চ্যানেল নির্বাচন প্লেয়ারের বর্তমান সেবাদাতা ব্যবহার করে; এটি যেকোনো ইচ্ছেমতো মিডিয়া URL আপলোড করে না। কনফিগারেশন প্লেব্যাক শুরু করে না বা টিভির প্রকৃত পাওয়ার নিয়ন্ত্রণ করে না।

## উন্নয়ন ও রিলিজ

Python 3.14 ব্যবহার করুন এবং `uv sync --locked` চালান, তারপর `uv run pytest -q`, `uv run ruff check .` ও `uv run ruff format --check .` চালান। পরীক্ষাগুলো বাড়ির ডিভাইসে সংযুক্ত না হয়ে প্রোটোকলের ব্যর্থতা, পরিচয় যাচাইয়ের তথ্য, জীবনচক্র এবং প্রকৃত HA এনটিটি পরিষেবা যাচাই করে। [রিলিজ প্রক্রিয়া](docs/releasing.md) দেখুন।

পাবলিক রিপোজিটরির সেটিংস [Terraform](https://github.com/4alvit/terraform-github-ha-homelab) দিয়ে পরিচালিত হয়। CI, [venus-os-ci-toolkit](https://github.com/victron-venus/venus-os-ci-toolkit)-এর নির্দিষ্ট রিভিশনে পিন করা ভাগাভাগি ওয়ার্কফ্লো ব্যবহার করে।
