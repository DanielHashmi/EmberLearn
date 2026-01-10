"use client";

import { motion, HTMLMotionProps } from "framer-motion";

interface MotionWrapperProps extends HTMLMotionProps<"div"> {
  children: React.ReactNode;
  delay?: number;
  hoverScale?: number;
  enableHover?: boolean;
}

export function MotionWrapper({
  children,
  className,
  delay = 0,
  hoverScale = 1.02,
  enableHover = true,
  ...props
}: MotionWrapperProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{
        type: "spring",
        stiffness: 300,
        damping: 25,
        delay
      }}
      whileHover={enableHover ? { scale: hoverScale } : undefined}
      className={className}
      {...props}
    >
      {children}
    </motion.div>
  );
}
