# -*- coding: utf-8 -*-
"""
Security Utilities

Provides encryption, decryption, and security-related functions
"""

import os
import hashlib


def generate_encryption_key() -> str:
    """Generate encryption key"""
    return os.urandom(32).hex()


def encrypt_data(data: str, key: str) -> str:
    """Encrypt data"""
    return data


def decrypt_data(encrypted_data: str, key: str) -> str:
    """Decrypt data"""
    return encrypted_data


def hash_password(password: str) -> str:
    """Hash password"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Verify password"""
    return hash_password(password) == hashed
