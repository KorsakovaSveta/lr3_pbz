from flask import Flask, render_template, request, redirect, url_for, flash
from owlready2 import *
from rdflib import Graph, URIRef, RDF
app = Flask(__name__)


# Загружаем онтологию OWL
onto = get_ontology('lr_2.owl').load()
g = Graph()
g.parse("lr_2.owl")
prefixs = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX ont: <http://example.org/ontology#>
"""
custom_ns = "http://www.semanticweb.org/acer/ontologies/2024/2/untitled-ontology-7#"
rdfs = "http://www.w3.org/2000/01/rdf-schema#"
rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
owl = "http://www.w3.org/2002/07/owl#"
classes = [cls.name for cls in onto.classes()]
individuals = [ind.name for ind in onto.individuals()]
# Маршрут Flask-приложения
@app.route('/')
def index():
    entities = []
    relationships = []
    
    # Получаем все классы
    for cls in onto.classes():
        entities.append({'name': cls.name, 'type': 'Class'})
    
    # Получаем все объекты (индивидуумы)
    for individual in onto.individuals():
        entities.append({'name': individual.name, 'type': 'Individual'})
    
    # Получаем все свойства и отношения
    for prop in onto.object_properties():
        entities.append({'name': prop.name, 'type': 'ObjectProperty'})
        
        # Получаем связи для каждого свойства или отношения
        for source in onto.individuals():
            values = prop[source]
            if values:
                if isinstance(values, list):
                    for value in values:
                        relationships.append({
                            'source': source.name,
                            'relation': prop.name,
                            'target': value.name if value else None
                        })
                else:
                    relationships.append({
                        'source': source.name,
                        'relation': prop.name,
                        'target': values.name if values else None
                    })
    
    # Рендерим HTML-шаблон и передаем списки сущностей и связей
    return render_template('index.html', entities=entities, relationships=relationships)

# @app.route('/add_subclass')
# def all_classes():
#     classes = []
#     # Получаем все классы
#     for cls in onto.classes():
#         classes.append(cls.name)
    
#     # Рендерим HTML-шаблон и передаем список классов
#     return render_template('classes.html', classes=classes)

# Маршрут Flask-приложения для обработки формы добавления подкласса
@app.route('/add_subclass', methods=['POST', 'GET'])
def add_subclass():

    if request.method == 'POST':
       
        # Получение данных из формы
        selected_class_name = request.form['selected_class']
        new_class_name = request.form['new_class']
        for individual in onto.individuals():
            if new_class_name == individual.name:
                error = "Уже существует объект класса с таким именем"
                return render_template('classes.html', error=error, classes=classes)
        for cls in onto.classes():
            if new_class_name == cls.name:
                error = "Уже существует класс с таким именем"
                return render_template('classes.html', error=error, classes=classes)  
        # Выбор класса, к которому нужно добавить новый класс
        selected_class = onto[selected_class_name]
        
        # Создание нового класса
        with onto:
            new_class = types.new_class(new_class_name, (selected_class,))

        classes.append(new_class.name)
        # Сохранение изменений в онтологии
        onto.save("lr_2.owl")

    return render_template('classes.html', classes=classes)

@app.route('/display_classes')
def display_classes():

    class_hierarchy = []
    # Iterate over classes and print their names and subclasses
    for cls in onto.classes():
        subclasses = []
        for subcls in cls.subclasses():
            subclasses.append(subcls.name)
        class_hierarchy.append({"name": cls.name, "subclasses": subclasses})

    return render_template('classes.html',classes=classes, class_hierarchy=class_hierarchy)
    #return render_template('hierarchy.html', classes_and_subclasses=classes_and_subclasses)

# @app.route('/add_individuals')
# def all_classes_and_individuals():
#     classes = []
#     # Получаем все классы
#     for cls in onto.classes():
#         classes.append(cls.name)
    
#     # Рендерим HTML-шаблон и передаем список классов
#     return render_template('individuals.html', classes=classes)

@app.route('/add_individuals', methods=['POST', 'GET'])
def add_individuals():

    if request.method == 'POST':
       
        # Получение данных из формы
        selected_class_name = request.form['selected_class']
        new_individual_name = request.form['new_individual']
        for individual in onto.individuals():
            if new_individual_name == individual.name:
                error = "Уже существует объект класса с таким именем"
                return render_template('classes.html', error=error, classes=classes)
        for cls in onto.classes():
            if new_individual_name == cls.name:
                error = "Уже существует класс с таким именем"
                return render_template('classes.html', error=error, classes=classes)  
        # Выбор класса, к которому нужно добавить новый класс
        selected_class = onto[selected_class_name]
        
        # Создание нового класса
        with onto:
            new_individual = selected_class(new_individual_name)

        
        # Сохранение изменений в онтологии
        onto.save("lr_2.owl")

    return render_template('individuals.html', classes=classes)

@app.route('/display_individuals')
def display_individuals():
    class_and_individuals, individuals =[], []
    # Iterate over classes and print their names and subclasses
    for cls in onto.classes():
        class_individuals = [ind.name for ind  in cls.instances()]
        subclasses = [subcls for subcls in cls.subclasses()]
        for subcls in subclasses:
            subclasses_individuals = [ind.name for ind in subcls.instances()]
        for ind in class_individuals:
            if ind not in subclasses_individuals:
                individuals.append(ind)
        class_and_individuals.append({"name": cls.name, "individuals": individuals})
        individuals = []
    return render_template('individuals.html',classes=classes, class_and_individuals=class_and_individuals)

# @app.route('/update_class_name')
# def update_class():
#     classes =[]
#     # Получаем все классы
#     for cls in onto.classes():
#         classes.append(cls.name)
    
#     # Рендерим HTML-шаблон и передаем список классов
#     return render_template('update.html', classes=classes)

@app.route('/update_class_name', methods=['POST', 'GET'])
def update_class_name():

    if request.method == 'POST':
       
        # Получение данных из формы
        selected_class_name = request.form['selected_class']
        new_class_name = request.form['new_class']
        for individual in onto.individuals():
            if new_class_name == individual.name:
                error = "Уже существует объект класса с таким именем"
                return render_template('classes.html', error=error, classes=classes)
        for cls in onto.classes():
            if new_class_name == cls.name:
                error = "Уже существует класс с таким именем"
                return render_template('classes.html', error=error, classes=classes)  
        # Выбор класса, к которому нужно добавить новый класс
        selected_class = onto[selected_class_name]
        
        selected_class.name = new_class_name
        onto.save("lr_2.owl")

    return render_template('update_classes.html', classes=classes)

@app.route("/display_classes_after_update")
def display_classes_after_update():
    classes_for_update =[]
    # Получаем все классы
    for cls in onto.classes():
        classes_for_update.append(cls.name)
    return render_template('update_classes.html',classes=classes, classes_for_update=classes_for_update)

@app.route('/update_individuals_name', methods=['POST', 'GET'])
def update_individuals_name():

    if request.method == 'POST':
       
        # Получение данных из формы
        selected_individual_name = request.form['selected_individual']
        new_individual_name = request.form['new_individual']
        for individual in onto.individuals():
            if new_individual_name == individual.name:
                error = "Уже существует объект класса с таким именем"
                return render_template('classes.html', error=error, classes=classes)
        for cls in onto.classes():
            if new_individual_name == cls.name:
                error = "Уже существует класс с таким именем"
                return render_template('classes.html', error=error, classes=classes)  
        # Выбор класса, к которому нужно добавить новый класс
        selected_individual = onto[selected_individual_name]
        
        selected_individual.name = new_individual_name
        onto.save("lr_2.owl")
    individuals = [ind.name for ind in onto.individuals()]
    return render_template('update_individuals.html', individuals=individuals)

@app.route("/display_individual_after_update")
def display_individuals_after_update():
    individuals_for_update =[]
    # Получаем все классы
    for indiv in onto.individuals():
        individuals_for_update.append(indiv.name)
    return render_template('update_individuals.html', individuals=individuals, individuals_for_update=individuals_for_update)

@app.route('/query_diseases', methods=['GET'])
def query_diseases():
    query_1 = prefixs + """ SELECT ?disease ?organ
    WHERE  {
        {?disease rdf:type <http://www.semanticweb.org/acer/ontologies/2024/2/untitled-ontology-7#аутоиммунные_заболевания_опорно-двигательного_аппарата>;
        <http://www.semanticweb.org/acer/ontologies/2024/2/untitled-ontology-7#поражаемая_структура> ?organ.}
        UNION
        {?disease rdf:type <http://www.semanticweb.org/acer/ontologies/2024/2/untitled-ontology-7#аутоиммунные_заболевания_опорно-двигательного_аппарата>;
        <http://www.semanticweb.org/acer/ontologies/2024/2/untitled-ontology-7#поражаемый_орган> ?organ.}
    } """

    query_2 = prefixs + """ SELECT ?disease_type ?disease ?symptoms ?difficulty
    WHERE {
    {?disease <http://www.semanticweb.org/acer/ontologies/2024/2/untitled-ontology-7#осложнение> ?difficulty;
    <http://www.semanticweb.org/acer/ontologies/2024/2/untitled-ontology-7#симптом> ?symptoms.}
    {?disease_type rdfs:subClassOf <http://www.semanticweb.org/acer/ontologies/2024/2/untitled-ontology-7#аутоиммунные_заболевания>.}
    {?disease rdf:type ?disease_type.}
    }
    """

    query_3 = prefixs + """ SELECT ?disease_type ((COUNT(?diseases)) AS ?count_diseases)
    WHERE {
    ?disease_type rdfs:subClassOf <http://www.semanticweb.org/acer/ontologies/2024/2/untitled-ontology-7#аутоиммунные_заболевания>.
    ?diseases rdf:type ?disease_type.
    }
    GROUP BY ?disease_type
    ORDER BY DESC(?count_diseases)
    """
    
    results = g.query(query_1)
    results_2 = g.query(query_2)
    results_3 = g.query(query_3)
    # Выводим результаты запроса
    diseases, symptoms_and_difficulty, count_diseases = [], [], []
    for row in results:
        subject = row['disease']
        object = row['organ']

        # Замена URI ссылок на названия объектов
        subject = subject.replace(custom_ns, "")
        object = object.replace(custom_ns, "")
        diseases.append({"disease": subject, "organ": object})

    for row in results_2:
        disease_type = row['disease_type']
        disease = row['disease']
        symptoms = row['symptoms']
        difficulty = row['difficulty']

        disease_type = disease_type.replace(custom_ns, "")
        disease = disease.replace(custom_ns, "")
        symptoms = symptoms.replace(custom_ns, "")
        difficulty = difficulty.replace(custom_ns, "")
        symptoms_and_difficulty.append({"disease_type": disease_type, "disease": disease, "symptoms": symptoms, "difficulty": difficulty})
    
    for row in results_3:
        disease_type = row['disease_type']
        count = row['count_diseases']

        disease_type = disease_type.replace(custom_ns, "")
        count = count.replace(custom_ns, "")
        count_diseases.append({"disease_type": disease_type, "count_diseases": count})
    return render_template('queries.html', diseases=diseases, symptoms_and_difficulty=symptoms_and_difficulty, count_diseases=count_diseases)
if __name__ == '__main__':
    app.run(debug=True) 