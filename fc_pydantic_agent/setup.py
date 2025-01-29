from setuptools import setup, find_packages

setup(
    name="fc_pydantic_agent",
    version="0.1.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'pydantic-ai>=0.0.20',
        'python-dotenv>=1.0.0',
        'loguru>=0.7.2'
    ],
    entry_points={
        'console_scripts': [
            'fc-dice-game=fc_pydantic_agent.examples.dice_game_example:main',
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="Flexible AI Agent Framework with Pydantic Validation",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/fc-pydantic-agent",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)