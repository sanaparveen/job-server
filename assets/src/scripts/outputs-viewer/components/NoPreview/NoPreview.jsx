import PropTypes from "prop-types";
import React from "react";
import { useFiles } from "../../context/FilesProvider";

function NoPreview({ error }) {
  const {
    state: { file },
  } = useFiles();

  return (
    <>
      {error ? <p>Error: {error}</p> : null}
      <p>We cannot show a preview of this file.</p>
      <p className="mb-0">
        <a href={file.url} rel="noreferrer noopener" target="_blank">
          Open file in a new tab &#8599;
        </a>
      </p>
    </>
  );
}

export default NoPreview;

NoPreview.propTypes = {
  error: PropTypes.string,
};

NoPreview.defaultProps = {
  error: null,
};
