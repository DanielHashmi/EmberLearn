"use client";

import { motion, AnimatePresence, useReducedMotion } from "framer-motion";
import { usePathname } from "next/navigation";

export default function Template({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const shouldReduceMotion = useReducedMotion();

  const variants = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 },
  };

  const transition = {
    type: "spring",
    stiffness: 300,
    damping: 28,
  };

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={pathname}
        variants={shouldReduceMotion ? {} : variants}
        initial="initial"
        animate="animate"
        exit="exit"
        transition={shouldReduceMotion ? { duration: 0 } : transition}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
}
