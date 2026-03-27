# Changelog

---

### Added
- finding_value parameter in `clean_values(data_input,finding_value)` find and remove rows that have this specific value
- finding_type parameter in `clean_values(data_input,finding_type)` find and remove rows that have this specific type (ex: str, int)
- condition parameter in `clean_values(data_input,condition : [operator, value] → ex: ['>=', 500])` applied only with finding_value or finding_type
---