/**
 * Huella criptográfica (fingerprint) de una tarjeta.
 *
 * Objetivo: poder detectar la MISMA tarjeta (para evitar duplicados) sin
 * almacenar el PAN. Se usa HMAC-SHA256 con un secreto de servidor
 * (CARD_FINGERPRINT_SECRET), no un hash simple del número.
 *
 * LIMITACIÓN: esto NO sustituye la tokenización de un proveedor de pagos ni
 * los controles PCI DSS. Es una referencia interna para correlación local.
 * Una integración real debe delegar el manejo del PAN a un proveedor
 * certificado y guardar únicamente el token que este devuelva.
 */

import { createHmac } from 'node:crypto';
import { env } from '../config/env';
import { normalizeCardNumber } from '../validation/card-validator';

/**
 * Genera la huella HMAC-SHA256 del PAN normalizado.
 * El PAN solo vive en memoria el tiempo necesario para calcular la huella.
 */
export function computeCardFingerprint(cardNumber: string): string {
  const normalized = normalizeCardNumber(cardNumber);
  return createHmac('sha256', env.CARD_FINGERPRINT_SECRET)
    .update(normalized)
    .digest('hex');
}
