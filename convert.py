from itertools import groupby
import yaml
import sys
import jinja2
import subprocess
import io
import os
import shutil

from pathlib import Path


tpl_dot = jinja2.Template("""

digraph recipe {

    bgcolor=transparent    
    node [color=transparent]

    {% for ing in ingredients %}
        "{{ ing.id }}" [id="{{ ing.id }}" label="{{ ing.label }}" shape=box class=ingredient]
    {%- endfor %}

    {% for act in activities %}
        "{{ act.id }}" [id="{{ act.id }}" label="{{ act.label }}" shape=box style=rounded class=activity]
    {%- endfor %}

    {% for edge in edges %}
        "{{ edge|join('" -> "') }}"
    {%- endfor %}
}
""")


tpl_index = jinja2.Template("""
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Jost:wght@500&display=swap');
            @import url(style.css);
        </style>
    </head>
    <body>
        <h1>Recipies</h1>
        <ul>
            {% for recipe in recipies %}
                <li><a href="{{ recipe }}">{{ recipe }}</a></li>
            {% endfor %}
        </ul>
    </body>
</html>
""")

tpl_recipie = jinja2.Template("""

<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Jost:wght@500&display=swap');
            @import url(style.css);
        </style>
    </head>
    <body>
        {{ svg|safe }}

        <script>
            const dependencies = {{ dependencies|tojson }};
            const nodes = document.querySelectorAll('svg .node');

            let done = new Set();

            for (let node of nodes) {
                node.addEventListener('click', evt => {
                    if (!done.has(node.id)) {
                        done.add(node.id);
                    }
                    else {
                        done.delete(node.id);
                    }
                    sync();
                })
            }

            function sync() {
                for (let node of nodes) {

                    if (done.has(node.id)) {
                        node.classList.add('done');
                        node.classList.remove('todo');
                    }
                    else {
                        node.classList.remove('done');
                        node.classList.toggle('todo',
                            (dependencies[node.id] || []).every(d => done.has(d))
                        
                         )
                    }
                }
            }

            sync();

        </script>
    </body>
</html>

""")


def render_recipe(filename, output):
    with open(filename) as fp:
        data = yaml.load(fp, Loader=yaml.Loader)

    def normalize(act):
        if isinstance(act, str):
            return {
                "id": act,
                "label": act,
            }
        else:
            return act

    dot = tpl_dot.render(
        ingredients=[normalize(ing) for ing in data['ingredients']],
        activities=[normalize(act) for act in data['activities']],
        edges=data['edges'])

    p = subprocess.run(['dot', '-Tsvg'],
                        input=dot.encode('utf-8'),
                        capture_output=True,
                        check=True)

    edges = sorted((right, left)
                        for edge in data['edges']
                        for left, right in zip(edge, edge[1:]))

    dependencies = {key: [r for l, r in lst] for key, lst in groupby(edges, key=lambda a: a[0])}

    with open(output, 'w') as fp:
        fp.write(    
            tpl_recipie.render(
                svg=p.stdout.decode('utf-8'),
                dependencies=dependencies))


def render_index(target, files):
    with open(target, "w") as fp:
        fp.write(tpl_index.render(recipies=files))


if __name__ == '__main__':
    builddir = Path("build")
    builddir.mkdir(parents=True, exist_ok=True)

    shutil.copyfile("style.css", builddir / "style.css")

    files = {source: builddir / source.with_suffix(".html").name
                for source
                in Path("recipies").glob("*.yml")}

    render_index(
        builddir / "index.html",
        [Path(file).name for file in files.values()])

    for source, target in files.items():
        render_recipe(source, target)

