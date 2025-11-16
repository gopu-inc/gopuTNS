gotn = {
    "REC": "FROM",
    "DO": "RUN",
    "BY": "COPY",
    "PUT": "ADD",
    "LOC": "WORKDIR",
    "SET": "ENV",
    "ASK": "ARG",
    "SPA": "EXPOSE",
    "GO": "CMD",
    "IN": "ENTRYPOINT",
    "BOX": "VOLUME",
    "WHO": "USER",
    "TAG": "LABEL",
    "TRIG": "ONBUILD",
    "SHL": "SHELL",
    "SIG": "STOPSIGNAL",
    "MED": "HEALTHCHECK"
}

def transpile_gopuTN_to_docker(lines):
    docker_lines = []
    for line in lines:
        parts = line.strip().split(" ", 1)
        if not parts:
            continue
        keyword = parts[0]
        args = parts[1] if len(parts) > 1 else ""
        docker_keyword = mapping.get(keyword, keyword)
        docker_lines.append(f"{docker_keyword} {args}")
    return "\n".join(docker_lines)

# Exemple d’utilisation
gopuTN_example = [
    "REC python:3.12",
    "LOC /app",
    "BY requirements.txt /app/",
    "DO pip install -r requirements.txt",
    "BY . /app",
    "SPA 8000",
    "GO [\"python\", \"main.py\"]"
]

print(transpile_gopuTN_to_docker(gopuTN_example))

