/**
 * Garde de navigation global.
 * ConsultationWorkflow enregistre un callback quand il est "dirty".
 * La sidebar et les autres composants appellent triggerGuard avant de naviguer.
 */
type GuardFn = (targetPath: string) => void;

let _guard: GuardFn | null = null;

export const registerNavigationGuard = (fn: GuardFn) => { _guard = fn; };
export const unregisterNavigationGuard = () => { _guard = null; };

/** Retourne true si la navigation est autorisée, false si bloquée (modal affiché). */
export const triggerNavigationGuard = (path: string): boolean => {
  if (_guard) { _guard(path); return false; }
  return true;
};
