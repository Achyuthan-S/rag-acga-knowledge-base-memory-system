from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip() for line in fh if line.strip() and not line.startswith("#")
    ]

setup(
    name="rag-knowledge-base",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Production-ready RAG with adaptive memory system and hybrid retrieval",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Achyuthan-S/rag-knowledge-base",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "full": [
            "neo4j>=5.0.0",
            "redis>=4.0.0",
            "psycopg2-binary>=2.9.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "acga-server=rag_knowledge_base.server:main",
            "acga-setup=rag_knowledge_base.setup:main",
        ],
    },
    include_package_data=True,
    package_data={
        "rag_knowledge_base": ["config/*.yaml", "prompts/*.txt"],
    },
    keywords="rag retrieval augmented generation memory knowledge base ai llm",
    project_urls={
        "Bug Reports": "https://github.com/Achyuthan-S/rag-knowledge-base/issues",
        "Source": "https://github.com/Achyuthan-S/rag-knowledge-base",
        "Documentation": "https://github.com/Achyuthan-S/rag-knowledge-base/blob/main/README.md",
        "Benchmarks": "https://github.com/Achyuthan-S/rag-knowledge-base/blob/main/BENCHMARKS.md",
    },
)
