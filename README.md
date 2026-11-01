# JobSkillGap

System, który pobiera publiczne oferty pracy IT z Greenhouse, Lever i Ashby, wyciąga z nich kompetencje, klasyfikuje oferty według profilu i poziomu, usuwa duplikaty, a użytkownikowi pokazuje, jakich kompetencji brakuje mu do wybranego profilu.

## Stos

Python 3.14, uv, FastAPI, SQLAlchemy 2.0 (sync), Alembic, PostgreSQL, Celery + Redis, Jinja2 + HTMX + Tailwind, spaCy, RapidFuzz, scikit-learn, pytest, ruff, Docker Compose.

## Uruchomienie

```bash
docker compose up -d --build
curl localhost:8000/health
docker compose exec web uv run alembic upgrade head
docker compose exec web uv run pytest
```

Lokalnie, bez Dockera:

```bash
uv sync
uv run ruff check .
uv run pytest
```

Zmienne środowiskowe: `DATABASE_URL`, `REDIS_URL`, `TEST_DATABASE_URL` (testy muszą wskazywać osobną bazę, nigdy deweloperską).



## Postęp

| Etap | Opis | Status |
|---|---|---|
| 0 | Fundament | [x] |
| 1 | Greenhouse + surowe dane | [ ] |
| 2 | Celery + Redis + odporność | [ ] |
| 3 | Lever i Ashby | [ ] |
| 4 | Zbiór referencyjny | [ ] |
| 5 | Ekstrakcja i normalizacja kompetencji | [ ] |
| 6 | Klasyfikacja profilu i poziomu | [ ] |
| 7 | Deduplikacja | [ ] |
| 8 | Statystyki i luka kompetencyjna | [ ] |
| 9 | Aplikacja webowa | [ ] |
| 10 | Wynagrodzenia, wdrożenie, domknięcie | [ ] |

---

## Etap 1: Pierwszy adapter + surowe dane (Greenhouse)

- [x] Tabele: `sources`, `companies`, `import_runs`, `raw_offers`, `job_offers` (migracja Alembic sprawdzona ręcznie)
- [x] Unikalny klucz `(source_id, external_id)` w `raw_offers` (widoczny w `\d raw_offers`)
- [x] Interfejs adaptera (`Protocol`: `fetch`, `external_id`, `to_unified`), sieć tylko w `fetch`
- [x] Fixture'y z prawdziwych odpowiedzi API w `tests/fixtures/greenhouse/`
- [x] Testy adaptera działają na fixture'ach, bez sieci
- [ ] `test_import_twice_creates_no_duplicates` przechodzi (drugi import: `new=0`, `unchanged=N`)
- [ ] `test_changed_payload_is_updated` przechodzi
- [ ] `test_every_offer_links_to_raw_payload` przechodzi
- [ ] Import ≥ 10 firm daje ≥ 500 ofert w `raw_offers`
- [ ] Ponowny import tych samych firm nie zmienia liczby wierszy
- [ ] `import_runs` zapisuje status i liczniki (new/updated/unchanged)
- [ ] Błąd jednej firmy nie przerywa importu pozostałych
- [ ] Notatka `docs/thesis-notes/01-greenhouse.md`

## Etap 2: Celery + Redis + odporność

- [ ] Usługi `worker` i `beat` w `docker-compose.yml`
- [ ] Task importu per źródło/firma
- [ ] Celery Beat uruchamia import cyklicznie (widoczne w logach i w `import_runs`)
- [ ] Test: jeden adapter rzuca wyjątek, pozostałe się kończą
- [ ] `import_runs.status` przyjmuje wartości `success` / `failed` / `partial`
- [ ] Liczniki nowe/zmienione/niezmienione zapisywane przy każdym runie
- [ ] Ponowne uruchomienie taska nie tworzy duplikatów
- [ ] Notatka `docs/thesis-notes/02-celery.md`

## Etap 3: Lever i Ashby

- [ ] Aktualne publiczne endpointy i limity sprawdzone w dokumentacji obu systemów (zapisane w notatce)
- [ ] Adaptery Lever i Ashby implementują ten sam interfejs co Greenhouse
- [ ] Fixture'y i testy na fixture'ach dla każdego źródła
- [ ] Idempotencja przetestowana dla każdego źródła
- [ ] W bazie ≥ 5000 ofert łącznie (lub wyraźnie widać, że dojdzie do tej liczby po dodaniu firm)
- [ ] Notatka `docs/thesis-notes/03-zrodla.md`

## Etap 4: Zbiór referencyjny

- [ ] Skrypt eksportuje losowe ~300 ofert do JSONL/CSV, losowanie z ziarnem zapisanym w repo (powtarzalne)
- [ ] Oznaczone ręcznie: kompetencje (nazwy kanoniczne), profil, poziom
- [ ] Podział na dev i test (np. 100/200), zapisany w plikach
- [ ] Pliki w `data/reference/`
- [ ] Walidacja schematu (Pydantic) w teście
- [ ] Notatka `docs/thesis-notes/04-zbior-referencyjny.md`

## Etap 5: Ekstrakcja i normalizacja kompetencji

- [ ] Słownik kompetencji w YAML (nazwa kanoniczna + aliasy)
- [ ] Dopasowanie z granicami słów / regex
- [ ] Reguły kontekstowe dla niejednoznacznych nazw (np. Go, R, C, Rust, Spark), po jednym teście na każdą regułę
- [ ] `uv run python -m job_skill_gap.eval skills` wypisuje precision / recall / F1 na dev i na test
- [ ] Wynik bazowy zapisany w notatce
- [ ] Każda wyekstrahowana kompetencja ma powiązanie z ofertą i pozycją w tekście
- [ ] Notatka `docs/thesis-notes/05-ekstrakcja.md`

## Etap 6: Klasyfikacja profilu i poziomu

- [ ] Normalizacja tytułu stanowiska
- [ ] Reguły: słowa kluczowe w tytule + kompetencje charakterystyczne dla profilu
- [ ] Taksonomia: Backend, Frontend, Fullstack, Data/ML, DevOps/Cloud, QA oraz Intern, Junior, Mid, Senior, Lead
- [ ] Kategoria `unclassified` dozwolona
- [ ] `eval classification` raportuje accuracy, F1 per klasa i macierz pomyłek (dev i test)
- [ ] Odsetek niesklasyfikowanych policzony i opisany w notatce
- [ ] Notatka `docs/thesis-notes/06-klasyfikacja.md`

## Etap 7: Deduplikacja

- [ ] W obrębie źródła: klucz zewnętrzny (z etapu 1)
- [ ] Między źródłami: blocking po znormalizowanej nazwie firmy
- [ ] RapidFuzz dla tytułu i lokalizacji, TF-IDF + cosine dla treści, łączny wynik z wagami
- [ ] Osobny zbiór oznaczonych par (kilkaset, z trudnymi przypadkami), podział dev/test
- [ ] Próg wybrany na dev
- [ ] P / R / F1 podane na teście
- [ ] Tabela lub wykres zależności precision/recall od progu
- [ ] Notatka `docs/thesis-notes/07-deduplikacja.md`

## Etap 8: Statystyki i luka kompetencyjna

- [ ] Częstość kompetencji per profil
- [ ] Współwystępowanie kompetencji
- [ ] Deklaracja kompetencji użytkownika (bez kont, w formularzu/sesji)
- [ ] Ranking luk wg częstości w ofertach danego profilu
- [ ] Endpointy API (`/profiles/{id}/skills`, `/gap`) z testami na małym, ręcznie policzonym zbiorze o znanym wyniku
- [ ] Notatka `docs/thesis-notes/08-luka.md`

## Etap 9: Aplikacja webowa

- [ ] Lista ofert z filtrami
- [ ] Statystyki profilu
- [ ] Formularz kompetencji użytkownika
- [ ] Widok luki
- [ ] Cały scenariusz (wybór profilu → zaznaczenie umiejętności → ranking luk) działa w przeglądarce na danych z bazy
- [ ] Notatka `docs/thesis-notes/09-web.md`

## Etap 10 (opcjonalnie): wynagrodzenia, wdrożenie, domknięcie

- [ ] Normalizacja waluty i okresu rozliczeniowego, bez przeliczania między formami zatrudnienia
- [ ] Zachowany rodzaj wynagrodzenia (brutto/netto) i forma zatrudnienia
- [ ] Wdrożenie online (działający link w README)
- [ ] README z diagramem architektury i wynikami ewaluacji (P/R/F1)
- [ ] Notatka końcowa i szlifowanie tekstu pracy

---

## Wymagania niefunkcjonalne (sprawdzane przez cały projekt)

- [ ] Powtarzalność przetwarzania (te same dane wejściowe dają ten sam wynik)
- [ ] Idempotentny import (unikalny klucz + test)
- [ ] Śledzenie pochodzenia każdego rekordu do surowego payloadu
- [ ] Odporność na błąd pojedynczego źródła (test)
- [ ] Automatyczne testy poszczególnych etapów przetwarzania w CI


## Etap 0: Fundament

- [x] `docker compose up` uruchamia usługi `web`, `db`, `redis`
- [x] `GET /health` zwraca 200 i sprawdza połączenie z bazą (`SELECT 1`)
- [x] `uv run pytest` przechodzi lokalnie
- [x] GitHub Actions uruchamia `ruff check` i `pytest` i jest zielony
- [x] `alembic upgrade head` działa, w bazie jest tabela `alembic_version`
- [x] Python przypięty do 3.14 (`.python-version`, `Dockerfile`)
- [x] `.venv`, `.env` w `.gitignore`; `.venv` w `.dockerignore`
