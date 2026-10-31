# Decyzje

## Aplikacja

**Nazwa robocza:** JobSkillGap

**Czym jest:** system, który pobiera publiczne oferty pracy IT z Greenhouse,
Lever i Ashby, wyciąga z nich kompetencje, klasyfikuje oferty według profilu
i poziomu, usuwa duplikaty, a użytkownikowi pokazuje, jakich kompetencji
brakuje mu do wybranego profilu.

**Co robi (zakres minimalny):**
1. Pobiera oferty przez publiczne API trzech źródeł (adaptery, jeden wspólny model).
2. Zapisuje surowy payload i ujednoliconą ofertę (identyfikowalność).
3. Ekstrahuje i normalizuje kompetencje (słownik + aliasy + regexy).
4. Klasyfikuje ofertę: profil (Backend, Frontend, Fullstack, Data/ML,
   DevOps/Cloud, QA) i poziom (Intern–Lead); dozwolone `unclassified`.
5. Deduplikuje oferty między źródłami.
6. Liczy częstość kompetencji per profil i współwystępowanie.
7. Użytkownik wybiera profil i zaznacza swoje kompetencje, a widzi ranking luk.
8. Wszystko dostępne w aplikacji webowej i przez API.
9. Skrypty ewaluacji liczą P/R/F1/accuracy na ręcznie oznaczonym zbiorze.

**Poza zakresem:**
- scrapowanie stron HTML (tylko publiczne API),
- modele ML do klasyfikacji (tylko reguły),
- konta użytkowników i logowanie (kompetencje w sesji/formularzu),
- przeliczanie wynagrodzeń między formami zatrudnienia,
- SPA (React itp.).

## Stos

| Obszar | Decyzja | Powód | Odrzucone |
|---|---|---|---|
| Język | Python 3.12 | znam, ekosystem NLP | - |
| Zależności | uv | szybki, lockfile | pip, poetry |
| Framework | FastAPI (sync endpointy) | typy, OpenAPI, znam | Django |
| ORM | SQLAlchemy 2.0 sync | Celery jest sync | async SQLAlchemy |
| Migracje | Alembic | standard dla SQLAlchemy | - |
| Baza | PostgreSQL 16 | JSONB na surowe dane, unikalne klucze | SQLite |
| Sterownik | psycopg 3 | aktualny | psycopg2 |
| Walidacja | Pydantic | wbudowany w FastAPI | - |
| Kolejka | Celery + Redis | cykliczny import, odporność na błędy | cron, RQ |
| Harmonogram | Celery Beat | - | - |
| Frontend | Jinja2 + HTMX + Tailwind | bez osobnego SPA | React |
| Ekstrakcja | słownik YAML + regex | powtarzalne, wyjaśnialne | modele ML/LLM |
| NLP | spaCy (PhraseMatcher, tylko jeśli potrzebny) | - | - |
| Podobieństwo | RapidFuzz (krótkie pola), scikit-learn TF-IDF + cosine (treść) | - | embeddingi |
| Testy | pytest, fixture'y z nagranych odpowiedzi API | brak zależności od sieci | - |
| Lint/format | ruff | - | black + flake8 |
| CI | GitHub Actions (ruff + pytest) | - | - |
| Uruchomienie | Dockerfile + docker compose (api, worker, beat, db, redis) | jedna komenda | - |

## Zasady projektu
- Import jest idempotentny: unikalny klucz `(source, external_id)`.
- Każdy rekord da się prześledzić do surowego payloadu.
- Błąd jednego źródła nie przerywa pozostałych.
- Zbiór referencyjny: podział dev/test, ziarno losowania zapisane w repo.
- Progi i reguły stroję na dev, wyniki raportuję na teście.

## Dziennik zmian
| Data | Decyzja | Status | Uwagi |
|---|---|---|---|
