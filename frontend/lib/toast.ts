import toast, { type Renderable } from 'react-hot-toast';
import { createElement } from 'react';
import { Coins } from 'lucide-react';

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
    icon: createElement(Coins, { size: 20, className: 'text-[#c7f464]' }),
    duration: 3000,
  });
};

export const showPetAction = (icon: Renderable, message: string) => {
  toast.success(message, {
    icon,
    duration: 2500,
  });
};

export { toast };
