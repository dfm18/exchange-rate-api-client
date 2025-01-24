from setuptools import setup


setup(
    name="exchange-rate-api-client",
    version="0.1.1",
    author="Daniel Fortich",
    author_email="fortichdaniel16@gmail.com",
    description="Unofficial client to interact with the Exchange Rate API V6",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/dfm18/exchange-rate-api-client",
    packages=["exchange_rate_api_client"],
    install_requires=["requests>=2.32", "pydantic>=2.10"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
