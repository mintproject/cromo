from setuptools import setup, find_packages

install_requires = [
"click",
"connexion",
"Flask-Cors",
"geojson",
"modelcatalog-api",
"openapi-schema-validator",
"openapi-spec-validator",
"Owlready2",
"PyYAML",
"requests",
"semver",
"numpy",
"Cython",
"Flask==2.0.1",
]

setup(name='cromo',
    version='1.1.3',
    packages=find_packages(),
    install_requires=install_requires,
)
