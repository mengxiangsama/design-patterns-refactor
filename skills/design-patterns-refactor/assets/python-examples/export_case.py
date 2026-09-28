"""A function-based refactoring example. Standard library only; no services."""
import base64
import gzip


def before(rows, compress=False, encode=False):
    payload = "\n".join(rows).encode("utf-8")
    if compress and encode:
        return base64.b64encode(gzip.compress(payload, mtime=0))
    if compress:
        return gzip.compress(payload, mtime=0)
    if encode:
        return base64.b64encode(payload)
    return payload


def gzip_bytes(payload):
    return gzip.compress(payload, mtime=0)


def apply_transforms(payload, transforms):
    for transform in transforms:
        payload = transform(payload)
    return payload


def after(rows, compress=False, encode=False):
    payload = "\n".join(rows).encode("utf-8")
    transforms = []
    if compress:
        transforms.append(gzip_bytes)
    if encode:
        transforms.append(base64.b64encode)
    return apply_transforms(payload, transforms)
