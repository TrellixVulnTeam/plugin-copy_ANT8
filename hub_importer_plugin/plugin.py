import logging
import os
import subprocess
import tarfile
import tempfile

default_logger = logging.getLogger(__name__)


def process(artifact_path, metadata, content_objs, logger=None):
    """Entry point for plugin, where group=post_load_plugin.

    This plugin called after galaxy_importer loads collection.
    """

    logger = logger or default_logger

    _check_module_doc_string(content_objs)

    _run_ansible_test(
        artifact_path=artifact_path,
        namespace=metadata.namespace,
        name=metadata.name,
        logger=logger,
    )


def _check_module_doc_string(content_objs):
    """Check modules have DOCUMENTATION string or fail import via exception."""
    # TODO(awcrosby): Implement


def _run_ansible_test(artifact_path, namespace, name, logger):
    """Runs ansible-test in local environment and logs output.

    --requirements option installs additional packages into environment.
    """
    logger.info('')
    logger.info('=== Running ansible-test sanity ===')

    ansible_root_bin = os.path.join(
        os.getenv('VIRTUAL_ENV'), 'src', 'ansible', 'bin')
    cmd = [
        'ansible-test sanity',
        '--requirements',
        '--python 3.7',
        '--failure-ok',
    ]
    absolute_cmd = os.path.join(ansible_root_bin, ' '.join(cmd))

    logger.debug(f'ansible_root_bin={ansible_root_bin}')
    logger.debug(f'absolute_cmd={absolute_cmd}')

    with tempfile.TemporaryDirectory() as temp_root:
        suffix = f'ansible_collections/{namespace}/{name}/'
        extract_dir = os.path.join(temp_root, suffix)
        os.makedirs(extract_dir)

        logger.debug(f'extract_dir={extract_dir}')
        logger.debug(
            f'os.path.exists(extract_dir)={os.path.exists(extract_dir)}')

        with tarfile.open(artifact_path, 'r') as pkg_tar:
            pkg_tar.extractall(extract_dir)

            proc = subprocess.Popen(
                absolute_cmd,
                cwd=extract_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                encoding='utf-8',
                shell=True,
            )

            for line in proc.stdout:
                if line.startswith('ERROR: '):
                    logger.error(line[7:].strip())
                elif line.startswith('WARNING: '):
                    logger.warning(line[9:].strip())
                else:
                    logger.info(line.strip())

            # NOTE --failure-ok makes returncode 0 for test errors
            if proc.wait() != 0:
                msg = 'An exception occured in ansible-test sanity'
                logger.error(msg)
