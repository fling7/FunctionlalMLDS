# v0.5 lossless round-trip evidence

Overall: **PASS**

Fixtures: 7/7

| Case | Structural equality | Object/array order | Locators | Agent aliases | Legacy levels | Main first |
|---|---:|---:|---:|---:|---:|---:|
| bestfit_career_fair | True | True | 12 | 5 | 6 | True |
| classroom_dinosaur | True | True | 12 | 4 | 6 | True |
| steinpilz_brand_room | True | True | 12 | 6 | 6 | True |
| cheese_factory_tradefair_booth_36f00adc | True | True | 12 | 6 | 6 | True |
| mldssteinpilz_e2e_1783611970 | True | True | 12 | 6 | 6 | True |
| mldssteinpilz_probe | True | True | 12 | 6 | 6 | True |
| mldssteinpilz_uidiag_abs_repair_1783611709 | True | True | 12 | 6 | 6 | True |

Export is fail-closed: non-empty `v2Extensions`, altered semantic projections, altered ledgers, invalid locator multiplicities and non-main first scenarios raise `RepresentabilityError`.
