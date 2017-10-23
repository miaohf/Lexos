import numpy as np
from flask import request, session, render_template, send_file, Blueprint

from lexos.helpers import constants as constants
from lexos.managers import utility, session_manager as session_manager
from lexos.views.base_view import detect_active_docs

# this is a flask blue print
# it helps us to manage groups of views
# see here for more detail:
# http://exploreflask.com/en/latest/blueprints.html
# http://flask.pocoo.org/docs/0.12/blueprints/
sim_blueprint = Blueprint('sim_query', __name__)


# Tells Flask to load this function when someone is at '/extension'
@sim_blueprint.route("/similarity", methods=["GET", "POST"])
def similarity():
    """Handles the similarity query page functionality.

    Returns ranked list of files and their cosine similarities to a comparison
    document.
    :return: a response object (often a render_template call) to flask and
    eventually to the browser.
    """
    # Detect the number of active documents.
    num_active_docs = detect_active_docs()
    file_manager = utility.load_file_manager()
    encoded_labels = {}
    labels = file_manager.get_active_labels()
    for i in labels:
        encoded_labels[str(i)] = labels[i]
    if request.method == 'GET':
        # 'GET' request occurs when the page is first loaded
        if 'analyoption' not in session:
            session['analyoption'] = constants.DEFAULT_ANALYZE_OPTIONS
        if 'similarities' not in session:
            session['similarities'] = constants.DEFAULT_SIM_OPTIONS
        return render_template(
            'similarity.html',
            labels=labels,
            encodedLabels=encoded_labels,
            docsListScore="",
            docsListName="",
            similaritiesgenerated=False,
            itm="similarity-query",
            numActiveDocs=num_active_docs)
    if 'gen-sims' in request.form:
        # 'POST' request occur when html form is submitted
        # (i.e. 'Get Graphs', 'Download...')
        score_name_data_frame = utility.generate_similarities(file_manager)

        docs_score = np.concatenate(score_name_data_frame.values)
        docs_name = np.array(score_name_data_frame.index)

        docs_list_score = '***'.join(str(score) for score in docs_score) \
                          + '***'
        docs_list_name = '***'.join(name for name in docs_name) + '***'

        session_manager.cache_analysis_option()
        session_manager.cache_sim_options()
        return render_template(
            'similarity.html',
            labels=labels,
            encodedLabels=encoded_labels,
            docsListScore=docs_list_score,
            docsListName=docs_list_name,
            similaritiesgenerated=True,
            itm="similarity-query",
            numActiveDocs=num_active_docs)
    if 'get-sims' in request.form:
        # The 'Download Matrix' button is clicked on similarity.html.
        session_manager.cache_analysis_option()
        session_manager.cache_sim_options()
        save_path, file_extension = utility.generate_sims_csv(file_manager)
        utility.save_file_manager(file_manager)
        return send_file(
            save_path,
            attachment_filename="similarity-query" + file_extension,
            as_attachment=True)