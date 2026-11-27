# М08 · Восстановление алгоритма

- Сценарий и его границы — TODO
- Исследованный SHA, версия среды и дата наблюдения — TODO
- Роли, входы, предусловия и тестовые данные — TODO
- Возвращаемые значения, ошибки и изменения состояния — TODO

## Трассировка

| Шаг | Файл:строка на исследованном SHA | Что передаётся | Что получается |
|---|---|---|---|
| 1 | Файл каталога | Запрос на открытие каталога  | Список книг |
| 2 | Файл карточки книги | ID выбранной книги  | Форма или запрос бронирования |
| 3 | Обработчик бронирования | ID книги и данные пользователя  | Полученные сервером параметры |
| 4 | Функция проверки | Входные данные | Результат проверки |

## Псевдокод

```text
TODO
```

## Диаграммы

- Блок-схема — [flowchart.png](flowchart.png) · редактируемый исходник — (https://viewer.diagrams.net/?tags=%7B%7D&lightbox=1&viewer-ui=classic&highlight=0000ff&edit=_blank&layers=1&nav=1&title=flowchart.drawio&dark=auto#R7Vtbb6M4FP41SLMPrbC5P4bQ7D7MSLPqamc6L5UHXIKGhKxDbvPr12AbbGiuTQOpUlUIH1+OL5+/c3xwNGM4Wb8kKdaMB00faFAv/o1hlKCYoAlNTNGEZgYahFqgawOgBUBzYfnUC4nPnkH5dEu5zeR3oKgE9SRi9Q3b+y/Jfcsh2e8fA+f52/PyV1FC1iz0T9Z/EjQbf8kinFJJtGZNAOh4rNFowySO6zBBTIQeUAsek9+880Dn0kUS4blSMM+yNE9mqjDMplMc5ooMEZKt1GIvWapqnaEYtwSPIUrb0m9JlI+Z1IVOLf8LJ/FYaAY2H/AEicJ8JPMxirKVJGrPo5hNkmX51ux6yoc4TaX14no0ODq+bjVMgqf525ubffn7pztynPDfu38WP3znab607l7RwUXzfCPmm2SLaYSLZoBm+KtxkuPHGQqL3BVFGJWN80nKs3nhr5gkE5xjwsWs0SVKF9JO8AKBfop4R9oJfvl84JUwyfFa6tzuoUvwxxntAtnQ9FjCg8lncVVjB4iZ5WoMAfWNinzEkRtXLR+6HLQMX5HzLBxkqnHU2irtlcwWJMT7QSCtOJ5Gg2Kj0lSYovk8CV9dZJqiPfYj/IIWaf4Z/cSpj8JfcZk9zNKsWH22m33aK7L5XtS4t0TyiTdQJoK1ktqI1DrJpWo09cQ7UbzXlYqEqMM5CZEY5zvGbbRB+XZ0WRwqBKcoT5bq6kiQs3ZA6pAu1B35miV0xWvsipY3ryticOCVDoPvHo2msVsjW4gTNPJtU830pTeZ0S07jiQP4UHiSFf4DxV3Ml9iWIytELIkI1FTpVj6pKPSP2nQTumQ/JB6B/Q9Lt7TDE2f6YTwLDqbcu4fvWFjp3dsbB7BxpdiWdOwFZ69B3uY9mOyoe1Rw6HY8qYxPz8hFkpdr/6j3rzSA/ujEKTVHUFykprnJJvGgqNK2pQdyZFEmEAlyUAq5klUaSm5xkiiw4ayvvBhC0/dE6J9RvfUahMnbfaRJ+c4ntAmH2qRv49XwwVZVrSqkiytys+7bgkuRHIpfRgFn+ywdku9a6XAW4mYLgDaSO3MCnKbH9fKdn4VG4JvAKjrpzE3Lc86+ja6dxrdeX+XuzUDH8akVEGcPpkU4UR3bgoamxV6e2DQvSVwb5ZAv/egYgvuQZW+2YMz2AMTeuewB4e3b5/U/rnsjWlsGe47hni2zcDV2xuvj/YmECeRMrbTN6tjCrz11+qIE1JPQncsJlctqa6G8apTKTukVtE+IMX5mGSkficsG4R7Y35l4a4Oq7ARjjaM/oEFnNFHcdo+yjuE+a70jHn+8F6DiowLHL2AtRvQV2sKATxiH9zwfRF8A7MRvjaaXz/eA+FNpWbTw7xejHf4TW+rvzc42eqbkocx4l/3mo2wKkNeso8B7aaP0IJbD3yEYyLaN27shhutC3zaays1G0qvlxs7jL0WLKhLxxYgPQ+59UBf5POU3JTZH17r380FcEx89sZr3fCa2aSYi/h8TbBeL691GOPbcyFhxw2uyq9zpPiOrlSpCrMXD/CPVX3hu5Zp7J7vRI+7wkI7DBhIbnvDohkSTEZSRVeq6PMLLFC+JwhbIUfYG1DYPbxMfUwA8GYEO3Lu3Q6MYAusV2sE4S241zeMN+/NGxf4jttU+WGC17Djy/qHG/bKSrtSeI4Z+UF1QV8bQm1wwn1WS03uu95KtfgdXmQVlH7Jb4NlmS2/5hMgrn83KZcpc8WvOlkGr1D/+vN/)
- UML-диаграмма последовательности — [sequence.png](sequence.png) · редактируемый исходник — TODO
- Условия, выходы и связь с проверками по ID — TODO

## Расхождения и вывод

TODO что подтверждено кодом и запуском, какие расхождения обнаружены, что проверять после изменений.
