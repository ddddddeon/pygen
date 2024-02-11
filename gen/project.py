import os
import shutil
import pybars
import subprocess
from enum import Enum, StrEnum
from typing import Optional
from os.path import abspath, dirname
from pydantic import BaseModel
from rich import print


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
        self.domain = self.get_domain()

    def create_dir(self) -> None:
        try:
            os.mkdir(self._project_dir)
        except FileExistsError as e:
            print(e)
            exit(1)

    def template(self, from_path: str, to_path: Optional[str] = None) -> None:
        if not to_path:
            to_path = from_path

        with open(f"{self._template_dir}/{from_path}", "r") as infile:
            source = infile.read()
            compiler = pybars.Compiler()
            template = compiler.compile(source)
            output = template({"name": self.name})
            with open(f"{self._project_dir}/{to_path}", "w") as outfile:
                outfile.write(output)

        print(to_path)

    def get_domain(self) -> Optional[str]:
        if self.domain is not None:
            return self.domain
        if self.lang not in [Lang.GO, Lang.JAVA]:
            return None

        with open(f"{self._template_dir}/domain") as domain_file:
            return domain_file.readline().strip()

    def copy_file(self, from_path: str, to_path: Optional[str] = None) -> None:
        if not to_path:
            to_path = from_path

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
        self.copy_file(".gitignore")

    def create_clang_format(self) -> None:
        self.copy_file(".clang-format")

    def create_python_project(self) -> None:
        self.create_dir()
        cwd = os.getcwd()
        os.chdir(self._project_dir)
        command = "virtualenv ."
        output = subprocess.check_output(command, shell=True)
        print(output)
        os.chdir(cwd)

    def create_rust_project(self) -> None:
        flags = {ProjectType.LIBRARY: "--lib", ProjectType.EXECUTABLE: "--bin"}
        command = f"cargo new {self.name} {flags[self.project_type]}"
        output = subprocess.check_output(command, shell=True)
        print(output)

        if self.project_type == ProjectType.EXECUTABLE:
            self.template("src/main.rs")
        open(f"{self._project_dir}/src/lib.rs", "w").close()

    def create_c_project(self) -> None:
        self.create_dir()
        self.create_clang_format()
        os.mkdir(f"{self._project_dir}/src")
        if self.project_type == ProjectType.EXECUTABLE:
            self.template("src/main.c")

    def create_cpp_project(self) -> None:
        self.create_dir()
        self.create_clang_format()
        os.mkdir(f"{self._project_dir}/src")
        if self.project_type == ProjectType.EXECUTABLE:
            self.template("src/main.cpp")

    def create_go_project(self) -> None:
        self.create_dir()
        if not self.domain:
            raise AttributeError("Domain not set")

        command = f"go mod init {self.domain}/{self.name}"
        cwd = os.getcwd()
        os.chdir(self._project_dir)
        output = subprocess.check_output(command, shell=True)
        print(output)
        self.template("main.go")
        os.chdir(cwd)

    def create_java_project(self) -> None:
        if not self.domain:
            raise AttributeError("Domain not set")

        command = f"mvn archetype:generate -DgroupId={self.domain}.{self.name} -DartifactId={self.name} -DarchetypeArtifactId=maven-archetype-quickstart -DinteractiveMode=false"
        cwd = os.getcwd()
        output = subprocess.check_output(command, shell=True)
        print(output)
        self.template("manifest.txt")

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
