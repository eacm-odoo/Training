/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';
import Dialog from 'web.Dialog';
import core from 'web.core';
import ajax from 'web.ajax';

const _t = core._t;

registerPatch({
	name: 'FileUploader',
	recordMethods: {
		async _performUpload({
			files
		}) {
			const attachmentLimit = await ajax.rpc("/web/dataset/call_kw/ir.config_parameter/get_param", {
				model: 'ir.config_parameter',
				method: 'get_param',
				args: ['fls_attachment.attachment_limit'],
				kwargs: {},
			});

			const limit = parseFloat(attachmentLimit) * 1024 ** 2; // converting to bytes
			const filesWithinLimit = [];
            const totalFilesCount = files.length;
			let exceededFilesCount = 0;

			for (const file of files) {
				if (limit && file.size > limit) {
					exceededFilesCount++;
				} else {
					filesWithinLimit.push(file);
				}
			}

			if (exceededFilesCount > 0) {
				let errorMessage = exceededFilesCount === 1 ?
					_t(`The file size exceeds the maximum limit of ${attachmentLimit} MB.`) :
					_t(`${exceededFilesCount} of these ${totalFilesCount} files exceed the size limit of ${attachmentLimit} MB. Uploading ${filesWithinLimit.length} files.`);

				Dialog.alert(this, errorMessage, {
					title: _t('Uploading Size Restriction'),
				});
			}
			if (filesWithinLimit.length) {
				return this._super({
					files: filesWithinLimit
				});
			}
		},
	}
});