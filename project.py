import shutil
import pybars
from enum import Enum, StrEnum
from typing import Optional
import os
from os.path import abspath, dirname
from pydantic import BaseModel
from rich import print
from rich.columns import Columns
from rich.tree import Tree


class ProjectType(Enum):
    LIBRARY = 0
    EXECUTABLE = 1

    @classmethod
    def _missing_(cls, value):
        value = value.lower()
        if value in ["lib", "library", "-l", "--lib", "-lib"]:
            return cls.LIBRARY
        else:
            return cls.EXECUTABLE


class Lang(StrEnum):
    PYTHON = "python"
    RUST = "rust"
    C = "c"
    CPP = "cpp"
    GO = "go"
    JAVA = "java"

    @classmethod
    def _missing_(cls, value):
        langs = {
            "py": cls.PYTHON,
            "python": cls.PYTHON,
            "rust": cls.RUST,
            "rs": cls.RUST,
            "c": cls.C,
            "cpp": cls.CPP,
            "cc": cls.CPP,
            "go": cls.GO,
            "golang": cls.GO,
            "java": cls.JAVA,
        }

        value = value.lower()
        if value not in langs:
            raise ValueError(f"Invalid language {value}! Valid languages: {langs()}")
        return langs[value]

    @classmethod
    def langs(cls) -> list[str]:
        return langs.keys()


class Project(BaseModel):
    lang: Lang
    name: str
    project_type: ProjectType
    domain: Optional[str] = None
    _template_dir: str | os.PathLike
    _project_dir: str | os.PathLike

    def __init__(self, **data):
        super().__init__(**data)
        proc_cwd = dirname(abspath(__file__))
        user_cwd = os.getcwd()
        self._template_dir = f"{proc_cwd}/templates/{self.lang.value}"
        self._project_dir = f"{user_cwd}/{self.name}"

    def create_dir(self) -> None:
        try:
            os.mkdir(self._project_dir)
        except FileExistsError as e:
            print(e)
            exit(1)

    def template(self, from_path: str, to_path: str) -> None:
        with open(f"{self._template_dir}/{from_path}", "r") as infile:
            source = infile.read()
            compiler = pybars.Compiler()
            template = compiler.compile(source)
            output = template({"name": self.name})
            with open(f"{self._project_dir}/{to_path}", "w") as outfile:
                outfile.write(output)

        print(to_path)

    def copy_file(self, from_path: str, to_path: str):
        shutil.copy(
            f"{self._template_dir}/{from_path}",
            f"{self._project_dir}/{to_path}",
        )
        print(to_path)

    def create_makefile(self) -> None:
        makefile_name = (
            "Makefile.lib"
            if self.project_type == ProjectType.LIBRARY
            else "Makefile.bin"
        )

        self.template(makefile_name, "Makefile")

    def create_gitignore(self) -> None:
        self.copy_file(".gitignore", ".gitignore")

    def create_clang_format(self) -> None:
        self.copy_file(".clang-format", ".clang-format")

    def create_python_project(self) -> None:
        self.create_dir()

    def create_rust_project(self) -> None:
        pass

    def create_c_project(self) -> None:
        self.create_dir()
        self.create_clang_format()
        os.mkdir(f"{self._project_dir}/src")
        if self.project_type == ProjectType.EXECUTABLE:
            self.template("src/main.c", "src/main.c")

    def create_cpp_project(self) -> None:
        self.create_dir()
        self.create_clang_format()
        os.mkdir(f"{self._project_dir}/src")
        if self.project_type == ProjectType.EXECUTABLE:
            self.template("src/main.cpp", "src/main.cpp")

    def create_go_project(self) -> None:
        self.create_dir()

    def create_java_project(self) -> None:
        pass

    def generate(self) -> None:
        match self.lang:
            case Lang.PYTHON:
                self.create_python_project()
            case Lang.C:
                self.create_c_project()
            case Lang.CPP:
                self.create_cpp_project()
            case Lang.RUST:
                self.create_rust_project()
            case Lang.GO:
                self.create_go_project()
            case Lang.JAVA:
                self.create_java_project()

        self.create_makefile()
        self.create_gitignore()
