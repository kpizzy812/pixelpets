import toast from 'react-hot-toast';
import { createElement } from 'react';

export const showSuccess = (message: string) => {
  toast.success(message);
};

export const showError = (message: string) => {
  toast.error(message);
};

export const showLoading = (message: string) => {
  return toast.loading(message);
};

export const dismissToast = (toastId: string) => {
  toast.dismiss(toastId);
};

export const showReward = (amount: number) => {
  toast.success(`+${amount} XPET`, {
    icon: createElement('img', {
      src: '/XPET.png',
      alt: 'XPET',
      style: { width: 20, height: 20, objectFit: 'contain' },
    }),
    duration: 3000,
  });
};

export const showPetAction = (imageKey: string, message: string) => {
  toast.success(message, {
    icon: createElement('img', {
      src: `/pets/${imageKey}.png`,
      alt: 'pet',
      style: { width: 24, height: 24, objectFit: 'contain' },
    }),
    duration: 2500,
  });
};

export { toast };
