# blinky - Türkçe Durum Özeti

Bu belge, projenin şu ana kadar ne yaptığını, şu an neye odaklandığını ve sırada ne olduğunu hızlı ve net şekilde anlatmak için hazırlandı.

## Proje Nedir?

Bu repo, STM32U585AI tabanlı STWIN.box kartı için kapalı döngü bir firmware doğrulama akışını tutuyor.
Bugünkü gerçek ve güvenilen çalışma yolu şu:

- `deploy.sh`
- `autofix.sh`
- `test_runner.py`

Bu zincir, firmware'i derlemek, cihaza yazmak ve UART üzerinden beklenen token'i görerek sonucu doğrulamak için kullanılıyor.

## Ne Yaptık?

Şu ana kadar yapılan temel işler:

- Layer A olarak adlandırılan ana akışı netleştirdik:
  - `deploy.sh` giriş noktası
  - `autofix.sh` tekrarlı derleme/flash/doğrulama orkestrasyonu
  - `test_runner.py` UART token doğrulama aracı
- Donanım doğrulamasında kullanılan temel token'i netleştirdik:
  - güncel kanonik token: `STWINBX1_ON_LINE`
  - `Kerem` yalnızca tarihsel kanıt
  - `SoS` ise scriptlerde kalan eski varsayılan davranış
- Layer A için daha güvenli ve daha izlenebilir bir iş akışı oluşturduk:
  - UART token, port, baud ve timeout bilgileri daha açık yazılıyor
  - `autofix.sh` ST-LINK ön kontrolü yapıyor
  - UART portuna erişim yoksa döngüye girmeden erken hata veriyor
- Başarılı gerçek-host kanıtlarını topladık ve kaydettik:
  - `logs/closed_loop_report_20260308_162608.md`
  - `logs/closed_loop_report_20260308_165114.md`
- LKG ve trusted baseline tanımını sıkılaştırdık:
  - kalıcı güvenilir durum, yalnızca canlı çalışma dizini değil
  - korunmuş raporlar
  - `versions/` altındaki snapshot'lar
  - kontrol dosyalarındaki kayıtlı durum
- Eski yardımcı script olan `tools/closed_loop_codex_verbose.py` dosyasını karantinaya aldık:
  - birincil yol değil
  - trusted Layer A parçası değil
  - şu an `py_compile` altında `TabError` veriyor
- Kod tabanını haritaladık ve `.planning/codebase/` altına şu dökümanları ekledik:
  - `STACK.md`
  - `ARCHITECTURE.md`
  - `STRUCTURE.md`
  - `CONVENTIONS.md`
  - `TESTING.md`
  - `INTEGRATIONS.md`
  - `CONCERNS.md`

## Şu An Ne Yapıyoruz?

Şu anki aktif faz:

- Phase 2c

Bu fazın amacı:

- stale helper script kaynaklı kafa karışıklığını azaltmak
- trusted baseline / LKG tanımını daha net hale getirmek
- canlı çalışma ağacının tek başına "kalıcı LKG" gibi düşünülmesini engellemek

Bugünkü odak, yeni firmware özelliği eklemek değil.
Odak, mevcut güvenilir akışı ve kanıt zincirini daha sağlam hale getirmek.

## Sırada Ne Var?

`TODO.md` dosyasına göre bir sonraki net aksiyon şu:

- `versions/` altındaki promoted snapshot'lar için açık ve küçük bir isimlendirme / kayıt kuralı tanımlamak

Bu neden gerekli?

- gelecekte hangi snapshot'in resmi olarak "promoted" olduğunu karıştırmamak için
- LKG kararlarını daha denetlenebilir yapmak için
- git olmayan bir repoda geri dönüş ve kanıt takibini daha güvenli tutmak için

## Projede Dikkat Edilmesi Gerekenler

- Repo kökünde şu an `.git` yoktu; yani bu proje şimdiye kadar git geçmişi olmadan ilerlemiş
- Donanım başarısı iddiaları operatör kanıtı olmadan yapılmamalı
- UART / ST-LINK / flash başarısı host ortamına bağlı
- `SoS` ile `STWINBX1_ON_LINE` arasındaki default farkı gelecekte temizlenmesi gereken bir konu
- `:Zone.Identifier` dosyaları gibi Windows kaynaklı yan dosyalar repoda gürültü oluşturuyor

## Repo İçindeki Önemli Dosyalar

- `AGENTS.md`: ajan kuralları ve yetki sınırları
- `TODO.md`: aktif iş ve bir sonraki net aksiyon
- `PROJECT_STATE.md`: doğrulanmış durum, riskler ve kanıtlar
- `RUNBOOK.md`: operatör akışı
- `planning.md`: gelecekteki Layer B hedefleri
- `BUILD_AGENT_TODO.md`: daha büyük dış sistem yol haritası
- `.planning/codebase/`: kod tabanı haritası

## Kısa Özet

Bu repo artık daha düzgün bir şekilde tarif edilmiş bir Layer A çalışma yoluna sahip.
Gerçek-host başarı kanıtları elde edilmiş durumda.
Bugünkü temel işimiz yeni davranış eklemekten çok, güvenilir baseline bilgisini, snapshot mantığını ve repo düzenini daha sağlam hale getirmek.
