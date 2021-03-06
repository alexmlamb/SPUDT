from importlib import import_module
from .train import train, evaluate_fid
from common.loaders import images
from common.util import get_args
from common.initialize import load_last_model


def parse_args(parser):
    parser.add_argument('--classifier-model-path', type=str, required=True)
    parser.add_argument('--classifier-model-type', type=str, required=True)
    parser.add_argument('--evalX-model-path', type=str, required=True)
    parser.add_argument('--evalY-model-path', type=str, required=True)
    parser.add_argument('--dataset-loc1', type=str, default='./data')
    parser.add_argument('--dataset-loc2', type=str, default='./data')
    parser.add_argument('--dataset1', type=str, default='mnist')
    parser.add_argument('--dataset2', type=str, default='svhn')
    parser.add_argument('--h-dim', type=int, default=64)
    parser.add_argument('--d-updates', type=int, default=5)
    parser.add_argument('--lr', type=float, default=1e-4)
    parser.add_argument('--beta1', type=float, default=0.5)
    parser.add_argument('--beta2', type=float, default=0.999)
    parser.add_argument('--z-dim', type=int, default=64)
    parser.add_argument('--radius', type=float, default=3.5)
    parser.add_argument('--gsxy', type=float, default=0)
    parser.add_argument('--gsyx', type=float, default=0)
    parser.add_argument('--gcxy', type=float, default=0)
    parser.add_argument('--gcyx', type=float, default=0)
    parser.add_argument('--gixy', type=float, default=0)
    parser.add_argument('--giyx', type=float, default=0)


def execute(args):
    dataset1 = getattr(images, args.dataset1)
    dataset2 = getattr(images, args.dataset2)
    train_loader1, valid_loader1, test_loader1, shape1, nc = dataset1(
        args.dataset_loc1, args.train_batch_size, args.test_batch_size, args.valid_split)
    train_loader2, valid_loader2, test_loader2, shape2, _ = dataset2(
        args.dataset_loc2, args.train_batch_size, args.test_batch_size, args.valid_split)
    args.loaders1 = (train_loader1, valid_loader1, test_loader1)
    args.loaders2 = (train_loader2, valid_loader2, test_loader2)
    args.shape1 = shape1
    args.shape2 = shape2

    model_definition = import_module('.'.join(('models', args.classifier_model_type, 'train')))
    model_parameters = get_args(args.classifier_model_path)
    model_parameters['nc'] = nc
    models = model_definition.define_models(shape1, **model_parameters)
    classifier = models['classifier']
    classifier = load_last_model(classifier, 'classifier', args.classifier_model_path)
    args.classifier = classifier

    model_definition = import_module('.'.join(('models', 'classifier', 'train')))
    model_parameters = get_args(args.evalX_model_path)
    model_parameters['nc'] = nc
    models = model_definition.define_models(shape1, **model_parameters)
    evalX = models['classifier']
    evalX = load_last_model(evalX, 'classifier', args.evalX_model_path)
    args.evalX = evalX

    model_definition = import_module('.'.join(('models', 'classifier', 'train')))
    model_parameters = get_args(args.evalY_model_path)
    model_parameters['nc'] = nc
    models = model_definition.define_models(shape1, **model_parameters)
    evalY = models['classifier']
    evalY = load_last_model(evalY, 'classifier', args.evalY_model_path)
    args.evalY = evalY

    train(args)
    evaluate_fid(args)
