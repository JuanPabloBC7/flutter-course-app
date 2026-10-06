/**
 * Controladores HTTP: traducen request/response <-> servicio.
 * No contienen lógica de negocio ni acceso a datos.
 */

import type { NextFunction, Request, Response } from 'express';
import * as service from '../services/credit-card-service';
import type { CreateCardInput, UpdateCardInput } from '../types/credit-card';
import type { CreateCardBody, UpdateCardBody } from '../validation/schemas';

/**
 * Envuelve un handler async para propagar errores al manejador central.
 * Evita try/catch repetido en cada controlador.
 */
function asyncHandler(
  fn: (req: Request, res: Response, next: NextFunction) => Promise<void>,
): (req: Request, res: Response, next: NextFunction) => void {
  return (req, res, next) => {
    fn(req, res, next).catch(next);
  };
}

/** GET /api/v1/credit-cards — lista tarjetas activas. */
export const listCards = asyncHandler(async (_req, res) => {
  const cards = await service.listActiveCards();
  res.status(200).json({ data: cards });
});

/** GET /api/v1/credit-cards/:id — obtiene una tarjeta por id. */
export const getCard = asyncHandler(async (req, res) => {
  const { id } = req.params as { id: string };
  const card = await service.getCardById(id);
  res.status(200).json({ data: card });
});

/** POST /api/v1/credit-cards — crea una tarjeta. */
export const createCard = asyncHandler(async (req, res) => {
  const body = req.body as CreateCardBody;
  const input: CreateCardInput = {
    userId: body.userId,
    cardNumber: body.cardNumber,
    expirationMonth: body.expirationMonth,
    expirationYear: body.expirationYear,
    cvv: body.cvv,
    creditLimit: body.creditLimit,
  };
  const card = await service.createCard(input);
  // Nota: el CVV y el PAN quedan solo en memoria durante esta solicitud.
  res.status(201).json({ data: card });
});

/** PATCH /api/v1/credit-cards/:id — actualiza creditLimit y/o status. */
export const updateCard = asyncHandler(async (req, res) => {
  const { id } = req.params as { id: string };
  const body = req.body as UpdateCardBody;
  const input: UpdateCardInput = {
    ...(body.creditLimit !== undefined ? { creditLimit: body.creditLimit } : {}),
    ...(body.status !== undefined ? { status: body.status } : {}),
  };
  const card = await service.updateCard(id, input);
  res.status(200).json({ data: card });
});

/** DELETE /api/v1/credit-cards/:id — eliminación lógica. */
export const deleteCard = asyncHandler(async (req, res) => {
  const { id } = req.params as { id: string };
  await service.deleteCard(id);
  // 204 sin cuerpo
  res.status(204).send();
});
