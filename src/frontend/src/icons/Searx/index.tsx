import React, { forwardRef } from "react";
import SvgSearxLogo from "./SearxLogo";

export const SearxIcon = forwardRef<SVGSVGElement, React.PropsWithChildren<{}>>(
  (props, ref) => {
    return <SvgSearxLogo ref={ref} {...props} />;
  },
);
