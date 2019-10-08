import logging
import os
import subprocess
import tarfile
import tempfile

default_logger = logging.getLogger(__name__)


def process(artifact_file, metadata, content_objs, logger=None):
    """Entry point for plugin, where group=post_load_plugin.

    This plugin called after galaxy_importer loads collection.
    """

    logger = logger or default_logger

    _check_module_doc_string(content_objs)

    _run_ansible_test(
        artifact_file=artifact_file,
        namespace=metadata.namespace,
        name=metadata.name,
        logger=logger,
    )


def _check_module_doc_string(content_objs):
    """Check modules have DOCUMENTATION string or fail import via exception."""
    # TODO(awcrosby): Implement


def _run_ansible_test(artifact_file, namespace, name, logger):
    """Runs ansible-test in local environment and logs output.

    --requirements option installs additional packages into environment.
    """
    logger.info('')
    logger.info('=== Running ansible-test sanity ===')

    cmd = [
        'ansible-test sanity',
        '--local',
        '--python 3.6',
        '--color yes',
        '--failure-ok',
    ]
    logger.debug(f'cmd={" ".join(cmd)}')

    with tempfile.TemporaryDirectory() as temp_root:
        suffix = f'ansible_collections/{namespace}/{name}/'
        extract_dir = os.path.join(temp_root, suffix)
        os.makedirs(extract_dir)

        artifact_file.seek(0)
        with tarfile.open(fileobj=artifact_file, mode='r') as pkg_tar:
            pkg_tar.extractall(extract_dir)

            proc = subprocess.Popen(
                ' '.join(cmd),
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
