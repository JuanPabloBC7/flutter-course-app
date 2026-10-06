/**
 * Definición de rutas de tarjetas bajo /api/v1/credit-cards.
 */

import { Router } from 'express';
import * as controller from '../controllers/credit-card-controller';
import { validateBody, validateParams } from '../middleware/validate';
import {
  cardIdParamSchema,
  createCardSchema,
  updateCardSchema,
} from '../validation/schemas';

export const creditCardRouter = Router();

// GET /api/v1/credit-cards
creditCardRouter.get('/', controller.listCards);

// POST /api/v1/credit-cards
creditCardRouter.post('/', validateBody(createCardSchema), controller.createCard);

// GET /api/v1/credit-cards/:id
creditCardRouter.get(
  '/:id',
  validateParams(cardIdParamSchema),
  controller.getCard,
);

// PATCH /api/v1/credit-cards/:id
creditCardRouter.patch(
  '/:id',
  validateParams(cardIdParamSchema),
  validateBody(updateCardSchema),
  controller.updateCard,
);

// DELETE /api/v1/credit-cards/:id
creditCardRouter.delete(
  '/:id',
  validateParams(cardIdParamSchema),
  controller.deleteCard,
);
