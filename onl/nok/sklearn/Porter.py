def port(model, to="java", method_name='predict', class_name='Tmp'):
    """Port a trained model in the syntax of a specific programming language.

    Parameters
    ----------
    :param to : String (default='java')
        The required syntax (e.g. 'java', 'c' or 'js' (or 'javascript')).

    :param model : Model object
        An instance of a trained model (e.g. DecisionTreeClassifier()).

    :param method_name : String (default='predict')
        The name of the prediction method.

    :param class_name : String (default='Tmp')
        The name of the environment class.
    """

    md_type, md_name = get_model_data(model)
    md_path = '.'.join(['onl.nok.sklearn', md_type, md_name])

    import os
    import sys
    sys.path.append(os.getcwd())

    module = __import__(md_path, globals(), locals(), [md_name], -1)
    md_class = getattr(module, md_name)
    md_method = getattr(md_class, 'port')
    return md_method(model, method_name=method_name, class_name=class_name)


def get_model_data(model):
    """Get data of the assigned model.

    Parameters
    ----------
    :param model : Model object
        An instance of a trained model (e.g. DecisionTreeClassifier()).

    :return md_type : String ['regressor', 'classifier']
        The model type.

    :return md_name : String
        The name of the used algorithm.
    """

    md_type = is_convertible_model(model)
    md_name = type(model).__name__
    return md_type, md_name


def get_convertible_classifiers():
    '''Get a list of convertible classifiers.'''

    import sklearn
    from sklearn.ensemble import weight_boosting
    return [
        sklearn.tree.tree.DecisionTreeClassifier,
        sklearn.ensemble.AdaBoostClassifier
    ]


def get_convertible_regressors():
    '''Get a list of all convertible regressors.'''
    return []


def is_convertible_model(model):
    """Check whether the model is a convertible classifier or regressor.

    Parameters
    ----------
    :param model : Model object
        An instance of a trained model (e.g. DecisionTreeClassifier()).

    See also
    --------
    onl.nok.sklearn.classifier.*, onl.nok.sklearn.regressor.*
    """

    classifiers = get_convertible_classifiers()
    is_convertible_clf = type(model) in classifiers
    if is_convertible_clf:
        return 'classifier'

    regressors = get_convertible_regressors()
    is_convertible_rgs = type(model) in regressors
    if is_convertible_rgs:
        return 'regressors'

    if not is_convertible_clf and not is_convertible_rgs:
        raise ValueError('The model is not an instance of a supported classifier or regressor.')
    return False


def main():
    import argparse
    import os

    parser = argparse.ArgumentParser(
        description='Port trained scikit-learn models to a low-level programming language.',
        epilog='More details on https://github.com/nok/sklearn-porter')
    parser.add_argument(
        'FILE',
        help='set the classifier in pickle format')
    parser.add_argument(
        '--to',
        choices=['c', 'java', 'js'],
        default='java',
        required=False,
        help='set target programming language')
    parser.add_argument(
        '--output',
        type=str,
        required=False,
        help='set the output path')

    args = vars(parser.parse_args())

    is_valid_input_file = lambda f: str(f).endswith('.pkl') and os.path.isfile(str(f))
    if is_valid_input_file(args['FILE']):

        # Target programming language:
        lang = str(args['to']) if str(args['to']) is not '' else 'java'

        # Input and output filename:
        inn = str(args['FILE'])
        out = inn.split('.')[-2] + '.' + lang

        if str(args['output']).endswith(('.c', '.java', '.js')):
            out = str(args['output'])
            lang = out.split('.')[-1].lower()

        from sklearn.externals import joblib
        with open(out, 'w') as file:
            model = joblib.load(inn)
            class_name = out.split('.')[-2].lower().title()
            file.write(port(model, to=lang, class_name=class_name))


if __name__ == '__main__':
    main()
