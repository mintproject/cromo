# CROMO
Contraint Reasoning Over MOdels. Cromo is built over the MINT platform, and it Recommends Models for a given combination of a Scenario, Time Period and a reagion. The Scenario provides a text keyword search to narrow down the list of matching models, and the Time Period & Region are used to match available input datasets for each of the models.

The Model Constraints themselves are written in SWRL (swirl), which stands for Semantic Web Rule Language.

Installation
------------
`pip install cromo`

Example Usage
-------------
* Clone the repository
* Go to the cromo directory
* Example run of cromo on rough terrain
`cromo search start Fire src/cromo/test/georgetown.geojson "2020-10-20" "2020-10-30"
* Example run of cromo on flat terrain
`cromo search start Fire src/cromo/test/whiterock.geojson "2021-03-01" "2021-03-31"`
