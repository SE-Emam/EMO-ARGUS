# المساهمة في ARGUS — حافظ على الريبو نظيفًا

> القاعدة الذهبية: **الزائر يرى القيمة في 10 ثوانٍ.** أي شيء للمطوّرين أو الأجنت أو المهام الداخلية → مكانه `docs/` أو `scripts/`، وليس الجذر.

## 1) أين تضع ملفاتك؟

| النوع | المكان الصح | ممنوع |
|---|---|---|
| ما يراه الزائر (تثبيت، قيمة، ديمو) | `README.md` فقط | ملفات تعليمات في الجذر |
| مواصفات الأجنت / التفاصيل المتقدمة | `docs/` | أي `*.md` جديد في الجذر |
| سكربتات تحقق / دخان | `scripts/` | ملفات مؤقتة في الجذر |
| اختبارات | `tests/` | — |
| تقارير مولّدة | `output/` (متجاهَلة، يبقى `.gitkeep` فقط) | commit لتقارير `*.md` مولّدة |
| بنية / قرارات معمارية | `docs/DECISIONS.md` (أضف ADR جديد) | تعليقات قرارات مبعثرة في الكود |

الجذر المسموح به فقط:

```
README.md  LICENSE  pyproject.toml  requirements.txt
argus_search.py  argus_mcp.py  argus_bridge.py  ARGUS-banner.jpeg
argus-chrome-extension/  argus-vscode-extension/  docs/  scripts/  tests/  output/.gitkeep  .github/  .gitignore
```

أي ملف خارج هذه القائمة (`SHA256SUMS`, `dist/`, `*.egg-info/`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`) يُرفض في الـ CI.

> فيتو الإضافة (ملزم): مجلدا `argus-chrome-extension/` و `argus-vscode-extension/` مساعدان مؤسسيان فقط — `host_permissions` / `bridgeUrl` حلقة محلية حصرًا (`127.0.0.1:8765`)، Manifest V3 صارم للكروم، وتوكن VS Code في `SecretStorage` فقط، ممنوع أي قدرات جمع مقيّدة خارج الـ CLI. يفرضها `check_extension_veto` في `scripts/check_hygiene.py`.

## 2) لغة الزائر (ممنوع AI Slop)

ممنوع في أي ملف يواجه المستخدم (`README.md`, `docs/*.md`, `argus_*.py --help`, `pyproject.toml`):

- `python argus_search.py` → استخدم `argus ...`
- `argus-search` → الصح `emo-argus` للتوزيعة و `argus` للأمر
- `sovereign-grade` / `sovereign deployment gate`
- أكواد داخلية: `(S1)` `(B6)` `Phase 1/2` `DRY` `God-function`
- `[Y]` → استخدم `Y` أو `yes` صريحة

قبل أي PR شغّل:

```bash
python scripts/check_hygiene.py
```

## 3) الأوامر الموحّدة

- التثبيت القانوني الوحيد: `pip install emo-argus`
- الأوامر بعد التثبيت: `argus plan|report|preview|modes|verify` + `argus-mcp`
- `pyproject.toml`: `description` تسويقي، `keywords` موجودة، `project.urls` (Homepage/Docs/Repo/Changelog) سليمة
- الكور بدون اعتمادات: `dependencies = []` — أي اعتماد جديد يحتاج ADR

## 4) سير العمل المحمي (لا تدفع على main أبدًا)

```bash
git checkout develop
# ... عدّل ...
python scripts/check_hygiene.py
python -m ruff check .
python -m pytest tests/ -q
python scripts/mcp_smoke_test.py
git commit -m "feat(scope): ماذا + لماذا"
git push origin develop
gh pr create --base main --head develop
# انتظر CI أخضر → squash merge → زامن develop
```

## 5) checklist الـ PR (موجودة أيضًا في template)

- [ ] `python scripts/check_hygiene.py` أخضر
- [ ] `ruff` + `pytest 10/10` + `smoke 3/3`
- [ ] لا ملفات جديدة في الجذر خارج القائمة البيضاء
- [ ] لا مصطلحات داخلية في واجهة المستخدم
- [ ] `README.md` ما زال: تثبيت 30 ثانية + قيمة + ديمو 60 ثانية
- [ ] `docs/CHANGELOG.md` محدَّث إذا تغيّر سلوك المستخدم
