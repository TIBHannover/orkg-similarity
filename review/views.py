from flask import abort
from flask.views import MethodView
from orkg import ORKG
from util import use_args_with
from ._params import ReviewGetParams
from models import VisualizationResponse as ObjectResponse
from flask import make_response
import datetime
import os


# TODO:
# * Support for ontology table section
# * Better support for figures within visualization sections

class ReviewAPI(MethodView):

    def __init__(self):
        super(ReviewAPI, self).__init__()
        self.orkg = ORKG(host=os.environ["ORKG_API_HOST"], simcomp_host=os.environ["ORKG_SIMCOMP_HOST"])

    @use_args_with(ReviewGetParams)
    def get(self, reqargs):
        resource_id = reqargs.get("resourceId")
        review_data = ObjectResponse.get_by_resource_id(resource_id)
        if not review_data:
            abort(404)

        statements = review_data.data['statements']
        review_resource_id = review_data.data['rootResource']
        review_resource = next((statement['subject'] for statement in statements if statement['subject']['id'] == review_resource_id), None)

        if "SmartReview" not in review_resource['classes']:
            abort(400, 'Request resource is not of class SmartReview')

        # prepare article metadata 
        title = next((statement['subject']['label'] for statement in statements if statement['subject']['id'] == review_resource_id), None)
        review_contribution = next((statement['object']['id'] for statement in statements if statement['predicate']['id'] == 'P31' and statement['subject']['id'] == review_resource_id), None)
        field = next((statement['object']['label'] for statement in statements if statement['predicate']['id'] == 'P30' and statement['subject']['id'] == review_resource_id), None)
        publication_date = next((statement['subject']['created_at'] for statement in statements if statement['subject']['id'] == review_resource_id), None)
        publication_date_parsed = datetime.datetime.strptime(publication_date, "%Y-%m-%dT%H:%M:%S.%fZ")
        publication_day = publication_date_parsed.strftime('%d')
        publication_month = publication_date_parsed.strftime('%m')
        publication_year = publication_date_parsed.strftime('%Y')
        authors = [statement['object']['label'] for statement in statements if statement['predicate']['id'] == 'P27' and statement['subject']['id'] == review_resource_id]
        authors_jats = "".join([generate_template_author(name) for name in authors])
        sections = [statement['object']['id'] for statement in statements if statement['predicate']['id'] == 'HasSection' and statement['subject']['id'] == review_contribution]
        sections_jats = ''

        # generate the sections, reverse for the right order
        for section_id in reversed(sections):
            section_resource = next((statement['object'] for statement in statements if statement['object']['id'] == section_id), None)
            section_title = section_resource['label']
            section_type = ' '.join(section_resource['classes']).replace("Section", "").strip().lower()
            section_content = ''

            # for text/content sections in Markdown
            if "Section" in section_resource['classes']:
                section_content = next((statement['object']['label'] for statement in statements if statement['subject']['id'] == section_id and statement['predicate']['id'] == 'hasContent'), None)

            # comparison section
            if "ComparisonSection" in section_resource['classes']:
                comparison_resource = next((statement['object'] for statement in statements if statement['subject']['id'] == section_id and statement['predicate']['id'] == 'HasLink'), None)
                if not comparison_resource:
                    continue
                comparison_id = comparison_resource['id']
                comparison_description = next((statement['object']['label'] for statement in statements if statement['subject']['id'] == comparison_id and statement['predicate']['id'] == 'description'), None)
                comparison_title = comparison_resource['label']
                comparison_table = self.orkg.contributions.compare_dataframe(comparison_id=comparison_id, like_ui=True).to_html()
                section_content = generate_template_section_comparison(comparison_title=comparison_title, comparison_description=comparison_description, comparison_table=comparison_table)

            # visualization section
            if "VisualizationSection" in section_resource['classes']:
                visualization_id = next((statement['object']['id'] for statement in statements if statement['subject']['id'] == section_id and statement['predicate']['id'] == 'HasLink'), None)
                if not visualization_id:
                    continue
                section_content = f'Visualization can be viewed via <a href="https://orkg.org/resource/{visualization_id}">the ORKG website</a>.'

            # property and resource sections 
            if "PropertySection" in section_resource['classes'] or "ResourceSection" in section_resource['classes']:
                section_entity_id = next((statement['object']['id'] for statement in statements if statement['subject']['id'] == section_id and statement['predicate']['id'] == 'HasLink'), None)
                if not section_entity_id:
                    continue
                entity_statements = [statement for statement in statements if statement['subject']['id'] == section_entity_id]

                rows = ''
                for statement in entity_statements:
                    rows += generate_template_entity_table_row(predicate_label=statement['predicate']['label'], object_label=statement['object']['label'])

                section_content = generate_template_entity_table(rows=rows)

            section_jats = generate_template_section(section_type=section_type, section_title=section_title, section_content=section_content)
            sections_jats += section_jats

        jats = generate_template_article(field=field, title=title, authors=authors_jats, publication_day=publication_day, publication_month=publication_month, publication_year=publication_year, sections=sections_jats)

        response = make_response(jats)
        response.headers['Content-Type'] = 'text/xml; charset=utf-8'
        return response


def generate_template_entity_table(rows):
    return f"""<table-wrap>
            <label>sdf</label>
            <caption>
                <title>asdf</title>
            </caption>
            <table>
                <thead>
                    <tr>
                        <th>Property</th>
                        <th>Value</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
        </table-wrap>
    """


def generate_template_entity_table_row(predicate_label, object_label):
    return f"""<tr>
            <td>{predicate_label}</td>
            <td>{object_label}</td>
        </tr>
    """


def generate_template_article(field, title, authors, publication_day, publication_month, publication_year, sections):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
        <article xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:ali="http://www.niso.org/schemas/ali/1.0">
            <front>
                <article-meta>
                    <article-categories>
                        <subj-group xml:lang="en">
                            <subject>{field}</subject>
                        </subj-group>
                    </article-categories>
                    <title-group>
                        <article-title>{title}</article-title>
                    </title-group>
                    <contrib-group content-type="author">{authors}</contrib-group>
                    <pub-date date-type="pub" iso-8601-date="{publication_year}-{publication_month}-{publication_day}">
                        <day>{publication_day}</day>
                        <month>{publication_month}</month>
                        <year>{publication_year}</year>
                    </pub-date>
                    <permissions id="permission">
                        <copyright-year>{publication_year}</copyright-year>
                        <copyright-holder>Open Research Knowledge Graph</copyright-holder>
                        <license>
                            <ali:license_ref>http://creativecommons.org/licenses/by-sa/4.0/</ali:license_ref>
                            <license-p>This work is licensed under a Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0)</license-p>
                        </license>
                    </permissions>
                </article-meta>
            </front>
            <body id="body">
                {sections}
            </body>
        </article>
    """


def generate_template_section(section_type, section_title, section_content):
    return f"""<sec sec-type="{section_type}">
            <title>{section_title}</title>
            <p>{section_content}</p>
        </sec>
    """


def generate_template_section_comparison(comparison_title, comparison_description, comparison_table):
    return f"""<table-wrap>
            <label>{comparison_title}</label>
            <caption>
                <title>{comparison_description}</title>
            </caption>
            {comparison_table}
        </table-wrap>
    """


def generate_template_author(name):
    return f"""<contrib contrib-type="person">
            <string-name>{name}</string-name>
        </contrib>
    """
